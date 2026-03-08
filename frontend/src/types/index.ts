/**
 * 100X Knowledge Agent - Type Definitions
 */

export interface TagCategory {
  [category: string]: string[];
}

export interface Tag {
  id: string;
  name: string;
  category: string;
}

// ============ Source Types ============

export enum SourceType {
  RSS = 'RSS',
  Twitter = 'Twitter',
  YouTube = 'YouTube'
}

export enum SourceStatus {
  Active = 'Active',
  Paused = 'Paused'
}

export interface Source {
  id?: number;
  type: SourceType | string;
  name: string;
  url?: string;
  enabled: boolean;
  category?: string;
  status?: SourceStatus; // UI helper
}

// ============ Feed Types ============

export interface FeedItem {
  id: number;
  title: string;
  source: string;
  url?: string;
  score: number;
  summary: string;
  keyInsights: string[];
  timestamp: string;
  readTime: string;
  tags: string[];
}

// ============ Note Types ============

export interface Note {
  id: number;
  title: string;
  preview: string;
  date: string;
  source: string;
  tags: string[];
  content?: string;          // 笔记完整内容（用于编辑）
  isFromFeed?: boolean;      // 是否来自 Feed 收藏
  feedItemId?: number;       // 对应的 Feed 项 ID
}

// ============ Common Types ============

export type NavLinkProps = {
  isActive: boolean;
};
