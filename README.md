# PolyVoice

**PolyVoice** — an API-first platform for AI-powered content creation and distribution across multiple channels.

## 🎯 Vision
PolyVoice is like having a creative newsroom of hundreds of authors working for you.  
You define the **project**, its **style** and **channels**, and the system will:  
- Generate multiple content variants using AI.  
- Let you refine and approve posts before publishing.  
- Schedule posts according to channel settings.  
- Distribute them across connected platforms (Telegram, X, LinkedIn, etc.).  

The long-term vision is to empower creators, while discouraging manipulative actors.  
PolyVoice introduces the idea of **AI-driven billing**:  
- Creative and socially valuable projects pay less (or even nothing).  
- Propaganda and scam-driven projects face prohibitively high costs.  
This makes the platform sustainable while supporting creativity.  

## 🚀 MVP Functionality
- **API-first** (REST API with Django REST Framework).  
- Custom user authentication (email-based).  
- **Projects** (top-level creative or business entities).  
- **Project Memberships** (users with roles: owner, editor, viewer).  
- **Channels** (distribution endpoints, starting with Telegram).  
- **Posts** (generation, moderation, scheduling, publishing).  
- Django Admin for management.  

## 🛠 Tech Stack
- **Backend**: Django + DRF  
- **Database**: PostgreSQL  
- **Queues**: Celery + Redis (for tasks & scheduling)  
- **AI**: OpenAI GPT (multi-provider planned)  
- **Integrations**: Telegram API (first channel, more to follow)  

## 🏗 Architecture

```mermaid
flowchart LR
    A["User / Dashboard"] -->|"Creates Project & Defines Style"| B["PolyVoice API"]
    B -->|"Generates Variants"| C["AI Engine (OpenAI / Claude / future providers)"]
    B -->|"Stores Data"| D["PostgreSQL"]
    B -->|"Queue Tasks"| E["Celery + Redis"]
    E -->|"Publishes"| F["Channels: Telegram, X, LinkedIn, ..."]
