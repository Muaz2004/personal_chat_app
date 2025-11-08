# Chat Application (Django + DRF + React + Tailwind CSS)

A real-time chat application with **private messaging**, **group chats**, and **user profiles with avatars** built using **Django REST Framework** for the backend and **React + Tailwind CSS** for the frontend.

---

## Features

### Authentication & Profile
- User registration and login with token-based authentication.
- User profile with avatar support.
- Update avatar via API.

### Private Messaging
- Send and receive private messages.
- Messages are marked as read when viewed.
- Unread message counts per sender.

### Group Chat
- Create groups and manage members (creator-only actions for add/remove).
- Leave a group; group is deleted if creator leaves.
- Group messages track read status per user.
- Unread message counts per group.

### Frontend
- Responsive UI built with **React** and **Tailwind CSS**.
- Chat windows for private and group messages.
- Display user avatars and unread message counts dynamically.

### API Security
- Token-based authentication.
- Permissions:
  - Only authenticated users can access messages and groups.
  - Only group creators can manage members.

---

## Installation

### Backend (Django + DRF)
1. Clone the repository:

`` bash
git clone https://github.com/your-username/chat-app.git
cd chat-app
Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


Install dependencies:

pip install -r requirements.txt


Apply migrations:

python manage.py makemigrations
python manage.py migrate


Create a superuser (optional):

python manage.py createsuperuser


Run the development server:

python manage.py runserver

Frontend (React + Tailwind CSS)

Navigate to frontend folder:

cd personalchat-frontend


Install dependencies:

npm install


Start development server:

npm start

API Endpoints
User

POST /api/register/ – Register user

POST /api/login/ – Login user

PATCH /api/avatar/ – Update avatar

GET /api/profiles/ – List user profiles

Private Messages

GET /api/messages/ – List all messages

POST /api/messages/ – Send message

GET /api/messages/conversation/?user_id=<id> – Conversation with user

GET /api/messages/unread/ – Unread counts per sender

Groups

GET /api/groups/ – List groups

POST /api/groups/ – Create group

POST /api/groups/<id>/add_member/ – Add member (creator only)

POST /api/groups/<id>/remove_member/ – Remove member (creator only)

POST /api/groups/<id>/leave_group/ – Leave group

Group Messages

GET /api/group_messages/?group_id=<id> – List messages in a group

POST /api/group_messages/ – Send group message

GET /api/group_messages/unread_counts/ – Unread counts per group

Models

User: Django's built-in user.

Profile: One-to-one with User, avatar support.

Message: Private messages with sender, receiver, timestamp, read status.

Group: Chat groups with creator and members.

GroupMessage: Group messages with read_by tracking per user.

Technologies

Backend: Django, Django REST Framework, Token Authentication

Frontend: React, Tailwind CSS

Database: SQLite (default), can switch to PostgreSQL

Image Uploads: User avatars

Notes

Make sure MEDIA_URL and MEDIA_ROOT are set for avatar uploads.

API returns JSON; any HTML responses indicate internal server errors.

Group messages are marked as read per user.
