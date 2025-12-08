// LimeStar Type Definitions

export interface Tag {
  id: number;
  name: string;
  color: string;
}

export interface TagWithCount extends Tag {
  count: number;
}

export interface Link {
  id: number;
  url: string;
  title: string;
  description: string;
  user_note: string | null;
  favicon_url: string | null;
  og_image_url: string | null;
  domain: string;
  created_at: string;
  updated_at: string;
  is_processed: boolean;
  tags: Tag[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface LinkListResponse extends PaginatedResponse<Link> {}
