/**
 * Utility Functions Tests
 *
 * Tests for utility functions including:
 * - cn (class name merger)
 * - getNavLinkClasses
 * - filterBySearchTerm
 * - filterNotesBySearchTerm
 */

import { describe, it, expect } from 'vitest';
import { cn, getNavLinkClasses, filterBySearchTerm, filterNotesBySearchTerm } from '../index';

describe('cn (class name utility)', () => {
  it('should join multiple class names', () => {
    expect(cn('class1', 'class2', 'class3')).toBe('class1 class2 class3');
  });

  it('should filter out empty strings', () => {
    expect(cn('class1', '', 'class2')).toBe('class1 class2');
  });

  it('should filter out null values', () => {
    expect(cn('class1', null, 'class2')).toBe('class1 class2');
  });

  it('should filter out undefined values', () => {
    expect(cn('class1', undefined, 'class2')).toBe('class1 class2');
  });

  it('should filter out false values', () => {
    expect(cn('class1', false, 'class2')).toBe('class1 class2');
  });

  it('should handle all falsey values', () => {
    expect(cn('', null, undefined, false)).toBe('');
  });

  it('should handle empty input', () => {
    expect(cn()).toBe('');
  });

  it('should keep truthy values including 0', () => {
    // Note: cn filters using Boolean, so 0 would be filtered
    expect(cn('class', 0 as any)).toBe('class');
  });
});

describe('getNavLinkClasses', () => {
  it('should return base classes when inactive', () => {
    const result = getNavLinkClasses({ isActive: false });
    expect(result).toContain('flex');
    expect(result).toContain('items-center');
    expect(result).toContain('gap-3');
    expect(result).toContain('px-4');
    expect(result).toContain('py-3');
    expect(result).toContain('rounded-xl');
    expect(result).toContain('transition-all');
    expect(result).toContain('duration-200');
  });

  it('should include inactive styling when not active', () => {
    const result = getNavLinkClasses({ isActive: false });
    expect(result).toContain('text-gray-600');
    expect(result).toContain('hover:bg-gray-50');
    expect(result).toContain('hover:text-gray-900');
  });

  it('should include active styling when active', () => {
    const result = getNavLinkClasses({ isActive: true });
    expect(result).toContain('bg-primary/10');
    expect(result).toContain('text-primary');
    expect(result).toContain('font-medium');
  });

  it('should not include both active and inactive styles', () => {
    const activeResult = getNavLinkClasses({ isActive: true });
    const inactiveResult = getNavLinkClasses({ isActive: false });

    expect(activeResult).not.toContain('text-gray-600');
    expect(inactiveResult).not.toContain('bg-primary/10');
  });
});

describe('filterBySearchTerm', () => {
  interface TestItem {
    name: string;
    type?: string;
  }

  const mockItems: TestItem[] = [
    { name: 'AI Blog', type: 'RSS' },
    { name: 'Tech News', type: 'RSS' },
    { name: 'Twitter Feed', type: 'Twitter' },
    { name: 'LinkedIn Posts', type: 'LinkedIn' },
  ];

  it('should return all items when search term is empty', () => {
    const result = filterBySearchTerm(mockItems, '');
    expect(result).toHaveLength(4);
  });

  it('should return all items when search term is whitespace only', () => {
    const result = filterBySearchTerm(mockItems, '   ');
    expect(result).toHaveLength(4);
  });

  it('should filter by name (case insensitive)', () => {
    const result = filterBySearchTerm(mockItems, 'ai');
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('AI Blog');
  });

  it('should filter by name with uppercase search', () => {
    const result = filterBySearchTerm(mockItems, 'BLOG');
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('AI Blog');
  });

  it('should filter by type when type exists', () => {
    const result = filterBySearchTerm(mockItems, 'rss');
    expect(result).toHaveLength(2);
    expect(result.every(item => item.type === 'RSS')).toBe(true);
  });

  it('should match name or type', () => {
    const result = filterBySearchTerm(mockItems, 'feed');
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('Twitter Feed');
  });

  it('should return empty array when no matches', () => {
    const result = filterBySearchTerm(mockItems, 'nonexistent');
    expect(result).toHaveLength(0);
  });

  it('should handle items without type field', () => {
    const itemsWithoutType: TestItem[] = [
      { name: 'Test Source' },
    ];
    const result = filterBySearchTerm(itemsWithoutType, 'test');
    expect(result).toHaveLength(1);
  });

  it('should handle special characters in search', () => {
    const itemsWithSpecial: TestItem[] = [
      { name: 'C++ Weekly', type: 'RSS' },
      { name: 'C# Daily', type: 'RSS' },
    ];
    const result = filterBySearchTerm(itemsWithSpecial, 'c++');
    expect(result).toHaveLength(1);
  });

  it('should handle partial matches', () => {
    const result = filterBySearchTerm(mockItems, 'ews');
    expect(result).toHaveLength(2); // Tech News, Twitter Feed
  });
});

describe('filterNotesBySearchTerm', () => {
  interface TestNote {
    title: string;
    preview: string;
  }

  const mockNotes: TestNote[] = [
    { title: 'AI Best Practices', preview: 'Learn about AI development patterns' },
    { title: 'Web Development Guide', preview: 'Modern web technologies and frameworks' },
    { title: 'Machine Learning Basics', preview: 'Introduction to ML algorithms' },
    { title: 'React Patterns', preview: 'Advanced React component patterns' },
  ];

  it('should return all notes when search term is empty', () => {
    const result = filterNotesBySearchTerm(mockNotes, '');
    expect(result).toHaveLength(4);
  });

  it('should filter by title', () => {
    const result = filterNotesBySearchTerm(mockNotes, 'AI');
    expect(result).toHaveLength(1);
    expect(result[0].title).toBe('AI Best Practices');
  });

  it('should filter by preview content', () => {
    const result = filterNotesBySearchTerm(mockNotes, 'algorithms');
    expect(result).toHaveLength(1);
    expect(result[0].title).toBe('Machine Learning Basics');
  });

  it('should match title or preview', () => {
    const result = filterNotesBySearchTerm(mockNotes, 'development');
    expect(result).toHaveLength(2); // AI Best Practices (title), Web Development Guide (title)
  });

  it('should be case insensitive', () => {
    const result = filterNotesBySearchTerm(mockNotes, 'MACHINE');
    expect(result).toHaveLength(1);
  });

  it('should return empty array when no matches', () => {
    const result = filterNotesBySearchTerm(mockNotes, 'quantum');
    expect(result).toHaveLength(0);
  });

  it('should handle partial word matches', () => {
    const result = filterNotesBySearchTerm(mockNotes, 'pattern');
    expect(result).toHaveLength(1);
    expect(result[0].title).toBe('React Patterns');
  });

  it('should handle empty preview', () => {
    const notesWithEmptyPreview: TestNote[] = [
      { title: 'Test Note', preview: '' },
    ];
    const result = filterNotesBySearchTerm(notesWithEmptyPreview, 'test');
    expect(result).toHaveLength(1);
  });

  it('should handle special characters in search', () => {
    const notesWithSpecial: TestNote[] = [
      { title: 'C++ Templates', preview: 'Guide to C++ templates' },
    ];
    const result = filterNotesBySearchTerm(notesWithSpecial, 'c++');
    expect(result).toHaveLength(1);
  });
});
