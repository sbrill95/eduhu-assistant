export interface Teacher {
  teacher_id: string;
  name: string;
}

export interface Chip {
  id: string;
  label: string;
  icon?: string;
}

export interface Attachment {
  type: 'file' | 'image';
  url: string;
  name: string;
  mimeType: string;
  size?: number;
}

export interface ChatMessage {
  id: string;
  role: 'assistant' | 'user';
  content: string;
  chips?: Chip[];
  attachments?: Attachment[];
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  last_message: string | null;
  updated_at: string;
}
