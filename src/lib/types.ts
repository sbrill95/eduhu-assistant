export interface Teacher {
  teacher_id: string;
  name: string;
  role: string;
  access_token: string;
  refresh_token: string;
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
  sources?: Array<{ index: number; title: string; url?: string }>;
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  last_message: string | null;
  updated_at: string;
}

export type ArtifactType = 'docx' | 'h5p' | 'audio' | 'image';
export interface Artifact {
  id: string;
  type: ArtifactType;
  title: string;
  url: string;
  /** For H5P: the access code */
  accessCode?: string;
  /** For H5P: the exercise page URL */
  pageUrl?: string;
  /** Message ID this artifact belongs to */
  messageId?: string;
}