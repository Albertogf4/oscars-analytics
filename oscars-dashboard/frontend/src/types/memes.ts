export interface MemeTemplate {
  id: string;
  name: string;
  text_slots: number;
  slot_names: string[];
  irony_type: string;
  description: string;
  max_chars_per_slot: number;
}

export interface GeneratedMeme {
  id: string;
  filename: string;
  url: string;
  template_id: string;
  category: 'pro_obaa' | 'anti_sinners';
  text_content: Record<string, string>;
  created_at: string;
}

export interface MemeListResponse {
  memes: GeneratedMeme[];
  total: number;
  categories: Record<string, number>;
}

export interface TemplateListResponse {
  templates: MemeTemplate[];
  total: number;
}

export interface GenerateRequest {
  category: 'pro_obaa' | 'anti_sinners';
  templates?: string[];
  num_memes?: number;
  tone?: 'savage' | 'playful' | 'sarcastic';
}

export interface GenerateResponse {
  success: boolean;
  memes: GeneratedMeme[];
  generation_time_ms: number;
  errors?: string[];
}

// Template Processing Types
export interface TemplateInfo {
  id: string;
  name: string;
  filename: string;
  text_slots: number;
  slot_names: string[];
  irony_type: string;
  description: string;
  max_chars_per_slot: number;
  thumbnail_url?: string;
}

export interface TemplateInfoListResponse {
  templates: TemplateInfo[];
  total: number;
}

export interface ProcessingStatus {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  current_stage?: string;
  progress_percent: number;
  stages_completed: string[];
  result?: TemplateProcessingResult;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateProcessingResult {
  visual_analysis: {
    panel_count: number;
    layout_type: string;
    characters_or_elements: string[];
    visual_contrast: string;
    panel_descriptions: string[];
    image_dimensions: {
      width: number;
      height: number;
    };
  };
  slot_detection: {
    text_slots: number;
    slot_names: string[];
    slot_descriptions: string[];
    max_chars_per_slot: number;
  };
  irony_analysis: {
    irony_type: string;
    irony_explanation: string;
    humor_mechanics: string;
    emotional_journey: string;
    meme_culture_context: string;
    tone: string;
    key_contrast_elements: string[];
  };
  metadata: {
    id: string;
    name: string;
    description: string;
    generator_function: string;
    filename: string;
  };
  examples: {
    example: Array<{ slot_name: string; text: string }>;
    pro_obaa_example: Array<{ slot_name: string; text: string }>;
    anti_sinners_example: Array<{ slot_name: string; text: string }>;
  };
  prompt: {
    template_prompt: string;
  };
  template_registry_entry?: Record<string, unknown>;
}

export interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface FinalizeRequest {
  job_id: string;
  metadata_overrides?: {
    id?: string;
    name?: string;
    description?: string;
  };
}

export interface FinalizeResponse {
  success: boolean;
  template_id: string;
  integration_status: Record<string, boolean | string>;
  message: string;
}
