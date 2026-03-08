/**
 * 100X Knowledge Agent - Utility Functions
 */

import type { NavLinkProps } from '../types';

// ============ Class Name Utilities ============

/**
 * Merge class names conditionally
 * A lightweight alternative to clsx/cn for this project
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

// ============ Navigation Style Utilities ============

/**
 * Generate navigation link classes based on active state
 * Used consistently across all NavLink components in Layout
 */
export function getNavLinkClasses({ isActive }: NavLinkProps): string {
  const baseClasses = 'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200';

  return cn(
    baseClasses,
    isActive
      ? 'bg-primary/10 text-primary font-medium'
      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
  );
}

// ============ Filter Utilities ============

/**
 * Filter sources by search term
 * Searches in name and type fields (case-insensitive)
 */
export function filterBySearchTerm<T extends { name: string; type?: string }>(
  items: T[],
  searchTerm: string
): T[] {
  if (!searchTerm.trim()) {
    return items;
  }

  const term = searchTerm.toLowerCase();
  return items.filter(item => {
    const nameMatch = item.name.toLowerCase().includes(term);
    const typeMatch = item.type ? item.type.toLowerCase().includes(term) : false;
    return nameMatch || typeMatch;
  });
}

/**
 * Filter notes by search term
 * Searches in title and preview fields (case-insensitive)
 */
export function filterNotesBySearchTerm<T extends { title: string; preview: string }>(
  items: T[],
  searchTerm: string
): T[] {
  if (!searchTerm.trim()) {
    return items;
  }

  const term = searchTerm.toLowerCase();
  return items.filter(item =>
    item.title.toLowerCase().includes(term) ||
    item.preview.toLowerCase().includes(term)
  );
}
