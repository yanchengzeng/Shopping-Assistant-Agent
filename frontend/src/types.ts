export interface Message {
  type: 'text' | 'json';
  content: string;
  sender: 'user' | 'assistant';
  imageUrl?: string;
}

export interface Product {
  name: string;
  description: string;
  brand: string;
  category: string;
  price: number;
  image_encoded?: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
} 