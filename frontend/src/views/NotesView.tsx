import { useState, useMemo, useEffect, useRef } from 'react';
import { Search, Plus, MessageSquare, Clock, Edit3, Save, X, Trash2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Note } from '../types';
import { filterNotesBySearchTerm } from '../utils';
import { useApp } from '../contexts/AppContext';

const NotesView = () => {
    const { notes, updateNote, deleteNote, addNote, selectedNoteId, setSelectedNoteId } = useApp();
    const [searchTerm, setSearchTerm] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState('');
    const editAreaRef = useRef<HTMLTextAreaElement>(null);

    // 获取当前选中的笔记
    const selectedNote = useMemo(() => {
        return notes.find(note => note.id === selectedNoteId);
    }, [notes, selectedNoteId]);

    // 当选中笔记变化时，更新编辑内容
    useEffect(() => {
        if (selectedNote) {
            setEditContent(selectedNote.content || selectedNote.preview || '');
            setIsEditing(false);
        }
    }, [selectedNote]);

    // 自动聚焦编辑框
    useEffect(() => {
        if (isEditing && editAreaRef.current) {
            editAreaRef.current.focus();
        }
    }, [isEditing]);

    // Keyboard Shortcuts (Cmd+S to Save)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 's') {
                e.preventDefault(); // Prevent browser save dialog
                if (isEditing && selectedNoteId) {
                    updateNote(selectedNoteId, editContent);
                    setIsEditing(false);
                }
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isEditing, selectedNoteId, editContent, updateNote]);

    // 过滤笔记
    const filteredNotes = useMemo(() => {
        return filterNotesBySearchTerm(notes, searchTerm);
    }, [notes, searchTerm]);

    // 选择笔记
    const handleSelectNote = (note: Note) => {
        setSelectedNoteId(note.id);
    };

    // 新建笔记
    const handleNewNote = () => {
        const newNote: Note = {
            id: Date.now(),
            title: '新笔记',
            preview: '开始编写你的笔记...',
            date: 'Today',
            source: '手动创建',
            tags: [],
            content: '# 新笔记\n\n开始编写你的笔记...'
        };

        addNote(newNote);
        setSelectedNoteId(newNote.id);
        setIsEditing(true);
    };

    // 保存编辑
    const handleSave = () => {
        if (selectedNoteId) {
            updateNote(selectedNoteId, editContent);
            setIsEditing(false);
        }
    };

    // 取消编辑
    const handleCancel = () => {
        if (selectedNote) {
            setEditContent(selectedNote.content || '');
        }
        setIsEditing(false);
    };

    // 删除笔记
    const handleDelete = () => {
        if (selectedNoteId && confirm('确定要删除这条笔记吗？')) {
            deleteNote(selectedNoteId);
            setSelectedNoteId(null);
            setIsEditing(false);
        }
    };

    return (
        <div className="flex h-full bg-background overflow-hidden relative">
            {/* Left Sidebar for Notes List */}
            <div className="w-1/3 min-w-[320px] max-w-sm bg-white border-r border-gray-100 flex flex-col h-full absolute md:relative z-10 transition-transform">
                <div className="p-6 border-b border-gray-100 px-6 py-5">
                    <div className="flex justify-between items-center mb-5">
                        <h1 className="text-2xl font-bold text-gray-900">Notes</h1>
                        <button
                            onClick={handleNewNote}
                            className="p-2 text-primary bg-primary/10 hover:bg-primary/20 rounded-lg transition-colors cursor-pointer"
                            title="新建笔记"
                        >
                            <Plus size={20} />
                        </button>
                    </div>

                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                        <input
                            type="text"
                            placeholder="Search notes..."
                            className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-100 rounded-lg focus:outline-none focus:bg-white focus:border-primary focus:ring-1 focus:ring-primary transition-all text-sm"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto w-full p-2 space-y-1">
                    {filteredNotes.length === 0 ? (
                        <div className="text-center py-8 text-gray-400">
                            <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />
                            <p>暂无笔记</p>
                            <p className="text-xs mt-1">从 Feed 收藏或手动创建</p>
                        </div>
                    ) : (
                        filteredNotes.map((note: Note) => (
                            <div
                                key={note.id}
                                onClick={() => handleSelectNote(note)}
                                className={`p-4 rounded-xl cursor-pointer transition-all w-full border ${selectedNoteId === note.id
                                    ? 'bg-primary/5 border-primary/20 shadow-sm'
                                    : 'bg-white border-transparent hover:bg-gray-50 hover:border-gray-100'
                                    }`}
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1 min-w-0">
                                        <h3 className={`font-semibold mb-1 truncate ${selectedNoteId === note.id ? 'text-primary' : 'text-gray-900'
                                            }`}>
                                            {note.title}
                                        </h3>
                                        <p className="text-sm text-gray-500 line-clamp-2 mb-3 leading-relaxed">
                                            {note.preview}
                                        </p>
                                    </div>
                                    {note.isFromFeed && (
                                        <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded whitespace-nowrap">
                                            收藏
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center justify-between mt-auto">
                                    <span className="text-xs font-medium text-gray-400 flex items-center gap-1">
                                        <Clock size={12} />
                                        {note.date}
                                    </span>
                                    <span className="text-xs font-medium px-2 py-0.5 bg-gray-100 rounded text-gray-500 truncate max-w-[100px]">
                                        {note.source}
                                    </span>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Main Content Area - Editor */}
            <div className="flex-1 bg-white md:bg-gray-50/30 flex flex-col h-full">
                {selectedNote ? (
                    <div className="flex-1 flex flex-col h-full overflow-hidden">
                        {/* 工具栏 */}
                        <div className="flex items-center justify-between px-8 py-4 border-b border-gray-100 bg-white">
                            <div className="flex items-center gap-2">
                                {isEditing ? (
                                    <>
                                        <button
                                            onClick={handleSave}
                                            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg hover:bg-teal-700 transition-colors text-sm font-medium"
                                        >
                                            <Save size={16} />
                                            保存
                                        </button>
                                        <button
                                            onClick={handleCancel}
                                            className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                                        >
                                            <X size={16} />
                                            取消
                                        </button>
                                    </>
                                ) : (
                                    <>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setIsEditing(true);
                                            }}
                                            className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                                        >
                                            <Edit3 size={16} />
                                            编辑
                                        </button>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDelete();
                                            }}
                                            className="flex items-center gap-1.5 px-3 py-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
                                        >
                                            <Trash2 size={16} />
                                            删除
                                        </button>
                                    </>
                                )}
                            </div>
                            {selectedNote.isFromFeed && (
                                <span className="text-xs text-gray-400">来自 Feed 收藏</span>
                            )}
                        </div>

                        {/* 编辑器/查看器 */}
                        <div
                            className="flex-1 overflow-y-auto p-8 md:p-12 cursor-text"
                            onClick={() => {
                                if (!isEditing) setIsEditing(true);
                            }}
                        >
                            {isEditing ? (
                                <textarea
                                    ref={editAreaRef}
                                    value={editContent}
                                    onChange={(e) => setEditContent(e.target.value)}
                                    onBlur={() => {
                                        // 失去焦点时自动保存并返回预览
                                        setTimeout(() => {
                                            handleSave();
                                        }, 100);
                                    }}
                                    className="w-full h-full min-h-[500px] bg-transparent border-none focus:outline-none focus:ring-0 resize-none font-mono text-sm leading-relaxed text-gray-800"
                                    placeholder="开始编写笔记..."
                                />
                            ) : (
                                <div className="max-w-4xl mx-auto">
                                    <div className="prose prose-slate lg:prose-lg max-w-none">
                                        <ReactMarkdown>
                                            {selectedNote.content || selectedNote.preview || '*Empty Note*'}
                                        </ReactMarkdown>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 p-8 md:p-12 max-w-4xl mx-auto w-full flex flex-col items-center justify-center text-center opacity-70">
                        <MessageSquare size={48} className="text-gray-300 mb-4" />
                        <h2 className="text-xl font-semibold text-gray-600 mb-2">Select a note to view</h2>
                        <p className="text-gray-400 max-w-md">
                            Choose a note from the list on the left to read, annotate, or expand upon your extracted knowledge.
                        </p>
                        <button
                            onClick={handleNewNote}
                            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-teal-700 transition-colors font-medium"
                        >
                            <Plus size={18} className="inline mr-2" />
                            新建笔记
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default NotesView;
