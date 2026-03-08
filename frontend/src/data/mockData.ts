/**
 * 100X Knowledge Agent - Mock Data
 */

import { Source, SourceType, SourceStatus, FeedItem, Note } from '../types';

// ============ Mock Sources ============

export const mockSources: Source[] = [
  {
    id: 1,
    type: SourceType.RSS,
    name: "TechCrunch",
    url: "https://techcrunch.com/feed/",
    status: SourceStatus.Active,
    enabled: true
  },
  {
    id: 2,
    type: SourceType.Twitter,
    name: "AI News Alerts",
    url: "@ai_news_daily",
    status: SourceStatus.Active,
    enabled: true
  },
  {
    id: 3,
    type: SourceType.RSS,
    name: "Hacker News",
    url: "https://news.ycombinator.com/rss",
    status: SourceStatus.Paused,
    enabled: false
  }
];

// ============ Mock Feed Items ============

export const mockFeedItems: FeedItem[] = [
  {
    id: 1,
    title: 'The Unreasonable Effectiveness of Recurrent Neural Networks',
    source: 'Karpathy Blog',
    score: 9.5,
    summary: 'A deep dive into how RNNs can generate text, with practical examples of character-level models learning to write Shakespeare, Wikipedia, and Linux source code.',
    keyInsights: [
      'RNNs can learn complex structures just by predicting the next character.',
      'Hidden states act as a memory of the sequence seen so far.'
    ],
    timestamp: '2 hours ago',
    readTime: '8 min read',
    tags: ['AI', 'Deep Learning', 'RNN']
  },
  {
    id: 2,
    title: 'Why we should stop using "technical debt"',
    source: 'Hacker News Top',
    score: 8.8,
    summary: 'An argument that "technical debt" is a misleading metaphor. Instead, we should talk about unmitigated risk, unfinished work, and lack of capabilities.',
    keyInsights: [
      'Debt implies a conscious choice to borrow against the future, but bad code is often just bad code.',
      'Reframing the problem helps communicate actual risks to stakeholders.'
    ],
    timestamp: '5 hours ago',
    readTime: '5 min read',
    tags: ['Software Engineering', 'Management']
  }
];

// ============ Mock Notes ============

export const mockNotes: Note[] = [
  {
    id: 1,
    title: 'Recurrent Neural Networks for Code Generation',
    preview: 'Looking at how well character-level RNNs can generate C code...',
    date: 'Today',
    source: 'Karpathy Blog',
    tags: ['Ideas', 'AI']
  },
  {
    id: 2,
    title: 'Reframing Technical Debt as Risk',
    preview: 'Instead of tech debt, we should discuss this with product managers as unmitigated risk to future feature delivery...',
    date: 'Yesterday',
    source: 'Hacker News Top',
    tags: ['Management']
  }
];
