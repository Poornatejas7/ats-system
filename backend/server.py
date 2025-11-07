from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import pdfplumber
from docx import Document
import io
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# HuggingFace Configuration
HF_API_KEY = os.environ['HUGGINGFACE_API_KEY']
HF_MODEL = os.environ['HUGGINGFACE_MODEL']
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ==================== AI Helper Functions ====================
async def generate_ai_content(prompt: str, max_tokens: int = 500) -> str:
    """Generate content using Llama model via HuggingFace API"""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(HF_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            return str(result)
        except Exception as e:
            logging.error(f"AI generation error: {str(e)}")
            return "Content generation temporarily unavailable."

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text
    except Exception as e:
        logging.error(f"PDF extraction error: {str(e)}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logging.error(f"DOCX extraction error: {str(e)}")
        return ""

# ==================== Models ====================
class ContactSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactSubmissionCreate(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

class JobPosting(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    department: str
    location: str
    type: str  # Full-time, Part-time, Contract, Internship
    description: str
    requirements: List[str]
    responsibilities: List[str]
    status: str = "active"  # active, closed
    posted_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class JobPostingCreate(BaseModel):
    title: str
    department: str
    location: str
    type: str
    description: str
    requirements: List[str]
    responsibilities: List[str]

class JobApplication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    job_title: str
    name: str
    email: EmailStr
    phone: str
    resume_text: str
    cover_letter: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, reviewing, shortlisted, rejected
    applied_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BlogPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    author: str
    tags: List[str] = []
    featured_image: Optional[str] = None
    seo_description: Optional[str] = None
    published: bool = False
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BlogPostCreate(BaseModel):
    title: str
    content: str
    author: str
    tags: List[str] = []
    featured_image: Optional[str] = None
    published: bool = False

class Testimonial(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    company: str
    position: Optional[str] = None
    content: str
    rating: int = 5
    avatar: Optional[str] = None
    featured: bool = False
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TestimonialCreate(BaseModel):
    client_name: str
    company: str
    position: Optional[str] = None
    content: str
    rating: int = 5
    avatar: Optional[str] = None

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    technologies: List[str]
    category: str
    image: Optional[str] = None
    client: Optional[str] = None
    completion_date: Optional[str] = None
    featured: bool = False
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    title: str
    description: str
    technologies: List[str]
    category: str
    image: Optional[str] = None
    client: Optional[str] = None
    completion_date: Optional[str] = None

class CaseStudy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    client: str
    challenge: str
    solution: str
    results: str
    ai_summary: Optional[str] = None
    technologies: List[str]
    image: Optional[str] = None
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CaseStudyCreate(BaseModel):
    title: str
    client: str
    challenge: str
    solution: str
    results: str
    technologies: List[str]
    image: Optional[str] = None

class AdminUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    password_hash: str
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    message: str

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

# ==================== Routes ====================
@api_router.get("/")
async def root():
    return {"message": "MasterSolis InfoTech API"}

# Contact Routes
@api_router.post("/contact", response_model=ContactSubmission)
async def submit_contact(input: ContactSubmissionCreate):
    contact_dict = input.model_dump()
    contact_obj = ContactSubmission(**contact_dict)
    
    doc = contact_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.contact_submissions.insert_one(doc)
    
    # Generate AI response email
    email_prompt = f"""Write a professional acknowledgment email for a contact form submission.
    Name: {contact_obj.name}
    Subject: {contact_obj.subject or 'General Inquiry'}
    Message: {contact_obj.message[:200]}
    
    Keep it brief, professional, and assure them we'll respond within 24-48 hours."""
    
    ai_response = await generate_ai_content(email_prompt, 200)
    
    return contact_obj

@api_router.get("/contact", response_model=List[ContactSubmission])
async def get_contacts():
    contacts = await db.contact_submissions.find({}, {"_id": 0}).to_list(1000)
    for contact in contacts:
        if isinstance(contact['timestamp'], str):
            contact['timestamp'] = datetime.fromisoformat(contact['timestamp'])
    return contacts

# Job Posting Routes
@api_router.post("/jobs", response_model=JobPosting)
async def create_job(input: JobPostingCreate):
    job_dict = input.model_dump()
    job_obj = JobPosting(**job_dict)
    
    doc = job_obj.model_dump()
    doc['posted_date'] = doc['posted_date'].isoformat()
    
    await db.job_postings.insert_one(doc)
    return job_obj

@api_router.get("/jobs", response_model=List[JobPosting])
async def get_jobs(status: Optional[str] = None):
    query = {"status": status} if status else {}
    jobs = await db.job_postings.find(query, {"_id": 0}).to_list(1000)
    for job in jobs:
        if isinstance(job['posted_date'], str):
            job['posted_date'] = datetime.fromisoformat(job['posted_date'])
    return jobs

@api_router.get("/jobs/{job_id}", response_model=JobPosting)
async def get_job(job_id: str):
    job = await db.job_postings.find_one({"id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if isinstance(job['posted_date'], str):
        job['posted_date'] = datetime.fromisoformat(job['posted_date'])
    return job

@api_router.put("/jobs/{job_id}", response_model=JobPosting)
async def update_job(job_id: str, input: JobPostingCreate):
    job = await db.job_postings.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_data = input.model_dump()
    await db.job_postings.update_one({"id": job_id}, {"$set": update_data})
    
    updated_job = await db.job_postings.find_one({"id": job_id}, {"_id": 0})
    if isinstance(updated_job['posted_date'], str):
        updated_job['posted_date'] = datetime.fromisoformat(updated_job['posted_date'])
    return updated_job

@api_router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    result = await db.job_postings.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

# Job Application Routes
@api_router.post("/applications")
async def submit_application(
    job_id: str = Form(...),
    job_title: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    cover_letter: Optional[str] = Form(None),
    resume: UploadFile = File(...)
):
    # Read and parse resume
    resume_content = await resume.read()
    resume_text = ""
    
    if resume.filename.lower().endswith('.pdf'):
        resume_text = extract_text_from_pdf(resume_content)
    elif resume.filename.lower().endswith(('.docx', '.doc')):
        resume_text = extract_text_from_docx(resume_content)
    else:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from resume")
    
    # AI Analysis of resume
    analysis_prompt = f"""Analyze this resume for the position of {job_title}.
    Resume Content: {resume_text[:1500]}
    
    Provide a JSON analysis with:
    1. skills: List of identified skills
    2. experience_years: Estimated years of experience
    3. education: Education level
    4. match_score: Score from 1-10 for job fit
    5. summary: Brief 2-sentence summary
    
    Return only valid JSON."""
    
    ai_analysis_raw = await generate_ai_content(analysis_prompt, 400)
    ai_analysis = {"raw_analysis": ai_analysis_raw, "resume_length": len(resume_text)}
    
    # Create application
    application = JobApplication(
        job_id=job_id,
        job_title=job_title,
        name=name,
        email=email,
        phone=phone,
        resume_text=resume_text,
        cover_letter=cover_letter,
        ai_analysis=ai_analysis
    )
    
    doc = application.model_dump()
    doc['applied_date'] = doc['applied_date'].isoformat()
    
    await db.job_applications.insert_one(doc)
    
    # Generate acknowledgment email
    email_prompt = f"""Write a professional job application acknowledgment email.
    Candidate: {name}
    Position: {job_title}
    
    Thank them for applying to MasterSolis InfoTech and inform them we'll review their application."""
    
    ai_email = await generate_ai_content(email_prompt, 200)
    
    return {"message": "Application submitted successfully", "application_id": application.id}

@api_router.get("/applications", response_model=List[JobApplication])
async def get_applications(job_id: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status
    
    applications = await db.job_applications.find(query, {"_id": 0}).to_list(1000)
    for app in applications:
        if isinstance(app['applied_date'], str):
            app['applied_date'] = datetime.fromisoformat(app['applied_date'])
    return applications

@api_router.get("/applications/{app_id}", response_model=JobApplication)
async def get_application(app_id: str):
    app = await db.job_applications.find_one({"id": app_id}, {"_id": 0})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if isinstance(app['applied_date'], str):
        app['applied_date'] = datetime.fromisoformat(app['applied_date'])
    return app

@api_router.put("/applications/{app_id}/status")
async def update_application_status(app_id: str, status: str):
    result = await db.job_applications.update_one(
        {"id": app_id},
        {"$set": {"status": status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Status updated successfully"}

# Blog Routes
@api_router.post("/blog", response_model=BlogPost)
async def create_blog(input: BlogPostCreate):
    blog_dict = input.model_dump()
    
    # Generate slug from title
    slug = blog_dict['title'].lower().replace(' ', '-').replace('/', '-')
    blog_dict['slug'] = slug
    
    # Generate excerpt and SEO description using AI
    excerpt_prompt = f"""Write a compelling 2-sentence excerpt for this blog post:
    Title: {blog_dict['title']}
    Content: {blog_dict['content'][:500]}"""
    
    seo_prompt = f"""Write an SEO-optimized meta description (max 160 characters) for:
    Title: {blog_dict['title']}
    Content: {blog_dict['content'][:300]}"""
    
    blog_dict['excerpt'] = await generate_ai_content(excerpt_prompt, 100)
    blog_dict['seo_description'] = await generate_ai_content(seo_prompt, 50)
    
    blog_obj = BlogPost(**blog_dict)
    
    doc = blog_obj.model_dump()
    doc['created_date'] = doc['created_date'].isoformat()
    doc['updated_date'] = doc['updated_date'].isoformat()
    
    await db.blog_posts.insert_one(doc)
    return blog_obj

@api_router.get("/blog", response_model=List[BlogPost])
async def get_blogs(published: Optional[bool] = None):
    query = {"published": published} if published is not None else {}
    blogs = await db.blog_posts.find(query, {"_id": 0}).to_list(1000)
    for blog in blogs:
        if isinstance(blog['created_date'], str):
            blog['created_date'] = datetime.fromisoformat(blog['created_date'])
        if isinstance(blog['updated_date'], str):
            blog['updated_date'] = datetime.fromisoformat(blog['updated_date'])
    return blogs

@api_router.get("/blog/{slug}", response_model=BlogPost)
async def get_blog(slug: str):
    blog = await db.blog_posts.find_one({"slug": slug}, {"_id": 0})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    if isinstance(blog['created_date'], str):
        blog['created_date'] = datetime.fromisoformat(blog['created_date'])
    if isinstance(blog['updated_date'], str):
        blog['updated_date'] = datetime.fromisoformat(blog['updated_date'])
    return blog

@api_router.post("/blog/{slug}/summarize")
async def summarize_blog(slug: str):
    blog = await db.blog_posts.find_one({"slug": slug}, {"_id": 0})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    summary_prompt = f"""Summarize this blog post in 3-4 bullet points:
    Title: {blog['title']}
    Content: {blog['content']}"""
    
    summary = await generate_ai_content(summary_prompt, 200)
    return {"summary": summary}

@api_router.delete("/blog/{slug}")
async def delete_blog(slug: str):
    result = await db.blog_posts.delete_one({"slug": slug})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return {"message": "Blog post deleted successfully"}

# Testimonial Routes
@api_router.post("/testimonials", response_model=Testimonial)
async def create_testimonial(input: TestimonialCreate):
    testimonial_obj = Testimonial(**input.model_dump())
    
    doc = testimonial_obj.model_dump()
    doc['created_date'] = doc['created_date'].isoformat()
    
    await db.testimonials.insert_one(doc)
    return testimonial_obj

@api_router.get("/testimonials", response_model=List[Testimonial])
async def get_testimonials(featured: Optional[bool] = None):
    query = {"featured": featured} if featured is not None else {}
    testimonials = await db.testimonials.find(query, {"_id": 0}).to_list(1000)
    for testimonial in testimonials:
        if isinstance(testimonial['created_date'], str):
            testimonial['created_date'] = datetime.fromisoformat(testimonial['created_date'])
    return testimonials

@api_router.post("/testimonials/generate")
async def generate_testimonial(input: AIRequest):
    """Generate or rephrase testimonial using AI"""
    prompt = f"""Based on this client feedback data, write a professional testimonial:
    {input.prompt}
    {input.context or ''}
    
    Make it authentic, specific, and impactful. Max 3 sentences."""
    
    testimonial = await generate_ai_content(prompt, 150)
    return {"generated_testimonial": testimonial}

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(input: ProjectCreate):
    project_obj = Project(**input.model_dump())
    
    doc = project_obj.model_dump()
    doc['created_date'] = doc['created_date'].isoformat()
    
    await db.projects.insert_one(doc)
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(category: Optional[str] = None):
    query = {"category": category} if category else {}
    projects = await db.projects.find(query, {"_id": 0}).to_list(1000)
    for project in projects:
        if isinstance(project['created_date'], str):
            project['created_date'] = datetime.fromisoformat(project['created_date'])
    return projects

@api_router.get("/projects/search")
async def search_projects(tech: Optional[str] = None):
    query = {}
    if tech:
        query["technologies"] = {"$in": [tech]}
    projects = await db.projects.find(query, {"_id": 0}).to_list(1000)
    for project in projects:
        if isinstance(project['created_date'], str):
            project['created_date'] = datetime.fromisoformat(project['created_date'])
    return projects

# Case Study Routes
@api_router.post("/case-studies", response_model=CaseStudy)
async def create_case_study(input: CaseStudyCreate):
    case_dict = input.model_dump()
    
    # Generate AI summary
    summary_prompt = f"""Summarize this case study in 2-3 sentences:
    Challenge: {case_dict['challenge']}
    Solution: {case_dict['solution']}
    Results: {case_dict['results']}"""
    
    case_dict['ai_summary'] = await generate_ai_content(summary_prompt, 150)
    
    case_obj = CaseStudy(**case_dict)
    
    doc = case_obj.model_dump()
    doc['created_date'] = doc['created_date'].isoformat()
    
    await db.case_studies.insert_one(doc)
    return case_obj

@api_router.get("/case-studies", response_model=List[CaseStudy])
async def get_case_studies():
    cases = await db.case_studies.find({}, {"_id": 0}).to_list(1000)
    for case in cases:
        if isinstance(case['created_date'], str):
            case['created_date'] = datetime.fromisoformat(case['created_date'])
    return cases

# AI Chatbot
@api_router.post("/chat")
async def chat(input: ChatMessage):
    prompt = f"""You are a helpful assistant for MasterSolis InfoTech, an IT consulting company.
    Services: Cloud Solutions, IT Services, Web Development, Full Stack Training, Projects, Internships.
    
    User question: {input.message}
    
    Provide a helpful, professional response."""
    
    response = await generate_ai_content(prompt, 250)
    return {"response": response}

# Admin Authentication
@api_router.post("/admin/register")
async def register_admin(input: AdminLogin):
    # Check if admin exists
    existing = await db.admin_users.find_one({"username": input.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(input.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin = AdminUser(
        username=input.username,
        email=f"{input.username}@mastersolis.com",
        password_hash=password_hash
    )
    
    doc = admin.model_dump()
    doc['created_date'] = doc['created_date'].isoformat()
    
    await db.admin_users.insert_one(doc)
    return {"message": "Admin registered successfully", "admin_id": admin.id}

@api_router.post("/admin/login")
async def login_admin(input: AdminLogin):
    admin = await db.admin_users.find_one({"username": input.username})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not bcrypt.checkpw(input.password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "admin_id": admin['id'], "username": admin['username']}

# Analytics
@api_router.get("/admin/analytics")
async def get_analytics():
    total_contacts = await db.contact_submissions.count_documents({})
    total_applications = await db.job_applications.count_documents({})
    total_jobs = await db.job_postings.count_documents({"status": "active"})
    total_blogs = await db.blog_posts.count_documents({"published": True})
    total_projects = await db.projects.count_documents({})
    
    # AI-generated summary
    summary_prompt = f"""Generate a brief analytics summary:
    - {total_contacts} contact submissions
    - {total_applications} job applications
    - {total_jobs} active job postings
    - {total_blogs} published blogs
    - {total_projects} projects
    
    Provide 2-3 insights about business health."""
    
    ai_summary = await generate_ai_content(summary_prompt, 150)
    
    return {
        "total_contacts": total_contacts,
        "total_applications": total_applications,
        "total_jobs": total_jobs,
        "total_blogs": total_blogs,
        "total_projects": total_projects,
        "ai_summary": ai_summary
    }

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()