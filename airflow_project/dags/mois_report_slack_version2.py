from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# --- 환경 설정 및 최적화 ---
# 모델을 매번 다운로드하지 않도록 로컬 캐시 경로를 지정합니다. 
# (Airflow 워커의 볼륨 마운트 경로로 설정하는 것이 좋습니다)
os.environ["HUGGINGFACE_HUB_CACHE"] = "/opt/airflow/cache/huggingface"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_huggingface_token"

DB_PATH = "/opt/airflow/data/chroma_db"
BASE_URL = "https://www.mois.go.kr"
LIST_URL = "https://www.mois.go.kr/frt/bbs/type001/commonSelectBoardList.do?bbsId=BBSMSTR_000000000336"

SLACK_WEBHOOK_URL = ("slack_webhook_url")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --- 1. 보고서 크롤링 및 PDF 텍스트 추출 ---
def extract_report_text(**kwargs):
    import PyPDF2
    print("🚀 최신 보고서 크롤링 시작...")
    
    response = requests.get(LIST_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    
    first_row = soup.select_one("table tbody tr:nth-of-type(1) a")
    if not first_row:
        raise Exception("게시글을 찾을 수 없습니다.")
        
    detail_url = urljoin(BASE_URL, first_row["href"])
    detail_resp = requests.get(detail_url)
    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
    
    file_list_div = detail_soup.find('div', class_='fileList')
    download_link_tag = file_list_div.find('a')
    full_download_url = urljoin(BASE_URL, download_link_tag['href'])
    modified_url = full_download_url.replace("fileSn=0", "fileSn=1")
    
    # [수정] 파일 경로 설정 및 디렉토리 확인
    pdf_path = "/tmp/today_report.pdf"
    
    # [수정] 다운로드 실행 (더 안전한 방식)
    print(f"📥 파일 다운로드 중: {modified_url}")
    with requests.get(modified_url, stream=True) as r:
        r.raise_for_status() # HTTP 에러 체크
        with open(pdf_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    # [수정] 파일이 실제로 생성되었는지 확인
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ 파일을 찾을 수 없습니다: {pdf_path}")
        
    print(f"✅ 다운로드 완료. 크기: {os.path.getsize(pdf_path)} bytes")

    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        print("✅ 텍스트 추출 완료")
    finally:
        # 에러가 나더라도 임시 파일은 삭제 시도
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
    kwargs['ti'].xcom_push(key='report_text', value=text)

# --- 2. Vector DB 생성 (신선도 유지) ---
def build_vector_store(**kwargs):
    text = kwargs['ti'].xcom_pull(key='report_text', task_ids='extract_report_task')
    
    # [중요] 기존 DB 삭제 (오늘 데이터만 유지하기 위함)
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print(f"🧹 기존 DB 삭제 완료: {DB_PATH}")
    
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100, separator='\n')
    split_texts = text_splitter.split_text(text)
    
    # 모델 로드 (캐시 경로 확인)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    vectorstore = Chroma.from_texts(
        texts=split_texts,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    vectorstore.persist()
    print("✅ 오늘자 보고서로 Vector DB 업데이트 완료")

# --- 3. AI Agent 질의 응답 ---
def run_ai_agent(**kwargs):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # LLM 설정 (실제 사용 가능한 Endpoint ID로 교체 권장)
    # llm_ep = HuggingFaceEndpoint(
    #     repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
    #     task="text-generation",
    #     max_new_tokens=512
    # )
    llm_ep = HuggingFaceEndpoint(repo_id="openai/gpt-oss-20b", task="conversational")
    llm = ChatHuggingFace(llm=llm_ep)
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        memory=memory
    )
    
    query = "오늘자 안전관리 일일상황보고서의 '기상 현황'과 '기상 전망' 내용을 불렛 형태로 요약해줘. 한국어로 답변해줘."
    response = qa_chain({"question": query})
    
    print("\n" + "="*50)
    print(f"🤖 AI Agent 응답:\n{response['answer']}")
    payload = {"text": (f"📌 *오늘의 안전관리상황 요약*\n```{response['answer']}```")}

    requests.post(
        SLACK_WEBHOOK_URL,
        json=payload,
        timeout=10,
    )
    print("="*50)

# --- DAG 정의 ---
with DAG(
    'mois_report_slack_version2',
    default_args=default_args,
    schedule='0 7 * * *', # 매일 오전 7시 실행
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id='extract_report_task',
        python_callable=extract_report_text,
    )

    t2 = PythonOperator(
        task_id='build_vector_db_task',
        python_callable=build_vector_store,
    )

    t3 = PythonOperator(
        task_id='query_ai_agent_task',
        python_callable=run_ai_agent,
    )

    t1 >> t2 >> t3