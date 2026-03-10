/**
 * 全局状态管理 - 100X Knowledge Agent
 * 管理收藏、笔记等共享状态
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Note, FeedItem, TagCategory } from '../types';
import { api } from '../services/api';

interface AppContextType {
  // 收藏的 Feed 项（会自动成为笔记）
  bookmarkedItems: FeedItem[];
  addBookmark: (item: FeedItem) => void;
  removeBookmark: (itemId: string) => void;
  isBookmarked: (itemId: string) => boolean;

  // 笔记（包含收藏的 Feed + 手动创建的笔记）
  notes: Note[];
  addNote: (note: Note) => void;
  updateNote: (noteId: number, content: string) => void;
  deleteNote: (noteId: number) => void;
  getNoteById: (noteId: number) => Note | undefined;

  // 当前选中的笔记
  selectedNoteId: number | null;
  setSelectedNoteId: (id: number | null) => void;

  // 标签管理
  tagCategories: TagCategory;
  setTagCategories: React.Dispatch<React.SetStateAction<TagCategory>>;
  loadTagCategories: () => Promise<void>;
  saveTagCategories: (newCategories: TagCategory) => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// 从 localStorage 加载数据
const loadFromStorage = <T,>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error loading ${key} from localStorage:`, error);
    return defaultValue;
  }
};

// 保存到 localStorage
const saveToStorage = <T,>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error saving ${key} to localStorage:`, error);
  }
};

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 初始化收藏项
  const [bookmarkedItems, setBookmarkedItems] = useState<FeedItem[]>(() =>
    loadFromStorage<FeedItem[]>('bookmarkedItems', [])
  );

  // 初始化笔记
  const [notes, setNotes] = useState<Note[]>(() =>
    loadFromStorage<Note[]>('notes', [])
  );

  // 当前选中的笔记
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(() => {
    const saved = localStorage.getItem('selectedNoteId');
    return saved ? JSON.parse(saved) : null;
  });

  // 标签种类
  const [tagCategories, setTagCategories] = useState<TagCategory>({});

  // 加载标签
  const loadTagCategories = useCallback(async () => {
    try {
      const data = await api.getTags();
      if (data && data.categories) {
        setTagCategories(data.categories);
      }
    } catch (error) {
      console.error('Failed to load tags:', error);
    }
  }, []);

  // 保存标签
  const saveTagCategories = async (newCategories: TagCategory) => {
    try {
      await api.updateTags({ categories: newCategories });
      setTagCategories(newCategories);
    } catch (error) {
      console.error('Failed to update tags:', error);
    }
  };

  useEffect(() => {
    loadTagCategories();
  }, [loadTagCategories]);

  // 持久化收藏项
  useEffect(() => {
    saveToStorage('bookmarkedItems', bookmarkedItems);
  }, [bookmarkedItems]);

  // 持久化笔记
  useEffect(() => {
    saveToStorage('notes', notes);
  }, [notes]);

  // 持久化选中的笔记
  useEffect(() => {
    saveToStorage('selectedNoteId', selectedNoteId);
  }, [selectedNoteId]);

  // 添加收藏
  const addBookmark = (item: FeedItem) => {
    if (!isBookmarked(item.id!)) {
      setBookmarkedItems(prev => [item, ...prev]);

      // 自动创建笔记
      const newNote: Note = {
        id: Date.now(),
        title: item.title,
        preview: item.summary,
        date: 'Today',
        source: item.source,
        tags: item.tags || [],
        content: `
# ${item.title}

**来源**: ${item.source || (item as any).source_detail}
**评分**: ${item.score || item.quality_score || item.analysis_score || 0}
**时间**: ${item.timestamp || item.published_at || item.created_at || "Unknown"}

## 摘要
${item.summary || item.extraction?.summary || item.content?.substring(0, 200) || ""}

## 关键洞察
${(item.keyInsights || item.key_insights || item.extraction?.key_insights || []).map((insight: string) => `- ${insight}`).join('\n')}

## 标签
${item.tags?.map((tag: string) => `#${tag}`).join(' ') || ''}
        `.trim(),
        isFromFeed: true,
        feedItemId: item.id
      };

      setNotes(prev => [newNote, ...prev]);
    }
  };

  // 移除收藏
  const removeBookmark = (itemId: string) => {
    setBookmarkedItems(prev => prev.filter(item => item.id !== itemId));

    // 同时删除对应的笔记
    setNotes(prev => prev.filter(note => note.feedItemId !== itemId));
  };

  // 检查是否已收藏
  const isBookmarked = (itemId: string): boolean => {
    return bookmarkedItems.some(item => item.id === itemId);
  };

  // 添加笔记
  const addNote = (note: Note) => {
    setNotes(prev => [note, ...prev]);
  };

  // 更新笔记
  const updateNote = (noteId: number, content: string) => {
    setNotes(prev =>
      prev.map(note =>
        note.id === noteId
          ? { ...note, content, preview: content.slice(0, 200) + '...' }
          : note
      )
    );
  };

  // 删除笔记
  const deleteNote = (noteId: number) => {
    setNotes(prev => prev.filter(note => note.id !== noteId));

    // 如果删除的是收藏的笔记，也取消收藏
    const noteToDelete = notes.find(n => n.id === noteId);
    if (noteToDelete?.feedItemId) {
      setBookmarkedItems(prev => prev.filter(item => item.id !== noteToDelete.feedItemId));
    }
  };

  // 根据 ID 获取笔记
  const getNoteById = (noteId: number): Note | undefined => {
    return notes.find(note => note.id === noteId);
  };

  return (
    <AppContext.Provider
      value={{
        bookmarkedItems,
        addBookmark,
        removeBookmark,
        isBookmarked,
        notes,
        addNote,
        updateNote,
        deleteNote,
        getNoteById,
        selectedNoteId,
        setSelectedNoteId,
        tagCategories,
        setTagCategories,
        loadTagCategories,
        saveTagCategories
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

// Hook for using the context
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
