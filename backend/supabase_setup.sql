-- ================================================
-- Supabase Setup Script for RAG Vector Store
-- Run this in your Supabase SQL Editor
-- ================================================

-- Enable pgvector extension (free on Supabase)
create extension if not exists vector;

-- Create documents table with vector embeddings
create table if not exists documents (
    id bigserial primary key,
    title text not null,
    content text not null,
    embedding vector(384),  -- MiniLM-L6-v2 produces 384-dim vectors
    metadata jsonb default '{}',
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Create index for fast similarity search
create index if not exists documents_embedding_idx 
on documents 
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Create index on metadata for filtering
create index if not exists documents_metadata_idx 
on documents 
using gin (metadata);

-- Function to search similar documents
create or replace function match_documents (
    query_embedding vector(384),
    match_threshold float default 0.5,
    match_count int default 5
)
returns table (
    id bigint,
    title text,
    content text,
    metadata jsonb,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        documents.id,
        documents.title,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) as similarity
    from documents
    where 1 - (documents.embedding <=> query_embedding) > match_threshold
    order by documents.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- ================================================
-- Conversation logs table (optional, for analytics)
-- ================================================

create table if not exists conversations (
    id bigserial primary key,
    session_id text not null,
    user_email text,
    messages jsonb default '[]',
    escalated boolean default false,
    ticket_id text,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- Index for session lookups
create index if not exists conversations_session_idx on conversations(session_id);

-- ================================================
-- Row Level Security (RLS) - Optional but recommended
-- ================================================

-- Enable RLS
alter table documents enable row level security;
alter table conversations enable row level security;

-- Allow public read access to documents (for RAG search)
create policy "Allow public read access to documents"
on documents for select
to anon
using (true);

-- Allow authenticated insert/update to documents
create policy "Allow authenticated insert to documents"
on documents for insert
to authenticated
with check (true);

-- For conversations, you might want more restrictive policies
-- This allows the API to read/write all conversations
create policy "Allow API access to conversations"
on conversations for all
to anon, authenticated
using (true)
with check (true);
