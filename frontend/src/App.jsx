import React, { useState, useEffect } from 'react';
import { Search, Loader2, Filter, ChevronLeft, ChevronRight, BookMarked, Building, Medal } from 'lucide-react';
import useDebounce from './hooks/useDebounce';
import { searchJournals, getFilterOptions } from './services/api';
import JournalCard from './components/JournalCard';

export default function App() {
    // ---- STATE MANAGEMENT ----
    const [searchTerm, setSearchTerm] = useState('');
    const [category, setCategory] = useState('');
    const [rank, setRank] = useState('');
    const [publisher, setPublisher] = useState('');
    
    // Đổ danh sách filter động từ DB
    const [dynamicPublishers, setDynamicPublishers] = useState([]);
    const [dynamicCategories, setDynamicCategories] = useState([]);

    const [data, setData] = useState({ data: [], total: 0, page: 1, limit: 20 });
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);

    const debouncedSearchTerm = useDebounce(searchTerm, 500);
    const ranks = ["Q1", "Q2", "Q3", "Q4", "Unranked"];

    // Lấy Filter Data khi vừa mở web
    useEffect(() => {
        const fetchFilters = async () => {
            const data = await getFilterOptions();
            setDynamicPublishers(data.publishers || []);
            setDynamicCategories(data.categories || []);
        };
        fetchFilters();
    }, []);

    // ---- FETCH API EFFECT ----
    useEffect(() => {
        const fetchResults = async () => {
            setLoading(true);
            try {
                // Xây dựng params cho API
                const params = { page, limit: 20 };
                if (debouncedSearchTerm) params.keyword = debouncedSearchTerm;
                if (category) params.category = category;
                if (rank) params.rank = rank;
                if (publisher) params.publisher = publisher; // Truyền thêm publisher query

                const responseData = await searchJournals(params);
                setData(responseData);
            } catch (error) {
                console.error("Lỗi khi lấy dữ liệu:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [debouncedSearchTerm, category, rank, publisher, page]);

    // Reset trở về trang 1 nếu người dùng thay đổi từ khóa tìm kiếm hoặc bộ lọc
    useEffect(() => {
        setPage(1);
    }, [debouncedSearchTerm, category, rank, publisher]);

    const totalPages = Math.ceil(data.total / data.limit) || 1;

    return (
        <div className="min-h-screen bg-gray-50/50 text-gray-900 font-sans selection:bg-blue-100">
            {/* --- HEADER & SEARCH SECTION --- */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
                <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                    
                    {/* Logo / Title */}
                    <div className="text-center mb-8">
                        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-600 mb-3 tracking-tight">
                            Journal Finder
                        </h1>
                        <p className="text-gray-500 font-medium">Explore & Ranking Scientific Journals (SJR & WoS)</p>
                    </div>

                    {/* Search Bar */}
                    <div className="max-w-4xl mx-auto relative mb-6 group">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                            <Search className={`h-5 w-5 transition-colors ${searchTerm ? 'text-blue-500' : 'text-gray-400'}`} />
                        </div>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Type to search journals by title..."
                            className="block w-full pl-12 pr-4 py-4 text-lg bg-gray-50 border border-gray-200 rounded-2xl focus:bg-white focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all shadow-inner placeholder:text-gray-400"
                        />
                        {/* Loading Spinner inside search bar */}
                        {loading && (
                            <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
                                <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                            </div>
                        )}
                    </div>

                    {/* Filter Bar */}
                    <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 items-center bg-gray-50/80 p-4 rounded-2xl border border-gray-100 shadow-sm">
                        <div className="flex items-center gap-2 px-2 text-gray-500 font-medium col-span-1 hidden md:flex">
                            <Filter size={18} />
                            <span>Filters</span>
                        </div>
                        
                        {/* Category Dropdown */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <BookMarked className="h-4 w-4 text-gray-400" />
                            </div>
                            <select
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                className="appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2.5 pl-9 pr-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-pointer text-sm font-medium"
                            >
                                <option value="">All Categories</option>
                                {dynamicCategories.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>

                        {/* Publisher Dropdown */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Building className="h-4 w-4 text-gray-400" />
                            </div>
                            <select
                                value={publisher}
                                onChange={(e) => setPublisher(e.target.value)}
                                className="appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2.5 pl-9 pr-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-pointer text-sm font-medium truncate"
                            >
                                <option value="">All Publishers</option>
                                {dynamicPublishers.map(p => <option key={p} value={p}>{p}</option>)}
                            </select>
                        </div>

                        {/* Rank Dropdown */}
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Medal className="h-4 w-4 text-gray-400" />
                            </div>
                            <select
                                value={rank}
                                onChange={(e) => setRank(e.target.value)}
                                className="appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2.5 pl-9 pr-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-pointer text-sm font-medium"
                            >
                                <option value="">All Ranks</option>
                                {ranks.map(r => <option key={r} value={r}>Rank: {r}</option>)}
                            </select>
                        </div>
                    </div>
                </div>
            </header>

            {/* --- MAIN CONTENT: RESULTS --- */}
            <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                
                {/* Result Meta */}
                <div className="flex justify-between items-end mb-6 border-b border-gray-200 pb-4">
                    <h2 className="text-xl font-bold text-gray-800">
                        Search Results {publisher && <span className="text-blue-600 font-medium ml-2 text-lg">by {publisher}</span>}
                    </h2>
                    <div className="text-sm font-medium text-gray-500 bg-white px-3 py-1 rounded-full border border-gray-200 shadow-sm">
                        Total {data.total.toLocaleString()} journals
                    </div>
                </div>

                {/* Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {data.data.map((journal) => (
                        <JournalCard 
                            key={journal.id || journal.ISSN || journal.Title} 
                            journal={journal} 
                        />
                    ))}
                </div>

                {/* Empty State */}
                {!loading && data.data.length === 0 && (
                    <div className="text-center py-24 bg-white rounded-2xl border border-dashed border-gray-300 mt-4">
                        <Search size={48} className="mx-auto text-gray-300 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-800">No journals found</h3>
                        <p className="text-gray-500 mt-2">Try adjusting your keywords or filters to find what you're looking for.</p>
                        <button 
                            onClick={() => { setSearchTerm(''); setCategory(''); setRank(''); setPublisher(''); }}
                            className="mt-6 px-6 py-2 bg-blue-50 text-blue-600 font-medium rounded-lg hover:bg-blue-100 transition"
                        >
                            Clear Filters
                        </button>
                    </div>
                )}

                {/* Pagination */}
                {data.total > 0 && (
                    <div className="mt-12 flex justify-center items-center gap-6">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1 || loading}
                            className="flex items-center gap-1 px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 hover:text-blue-600 disabled:opacity-50 disabled:hover:bg-white disabled:hover:text-gray-900 disabled:cursor-not-allowed font-medium transition-all shadow-sm"
                        >
                            <ChevronLeft size={18} /> Prev
                        </button>
                        
                        <span className="text-sm font-semibold text-gray-600">
                            Page {page} <span className="font-normal text-gray-400">/</span> {totalPages}
                        </span>

                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page >= totalPages || loading}
                            className="flex items-center gap-1 px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 hover:text-blue-600 disabled:opacity-50 disabled:hover:bg-white disabled:hover:text-gray-900 disabled:cursor-not-allowed font-medium transition-all shadow-sm"
                        >
                            Next <ChevronRight size={18} />
                        </button>
                    </div>
                )}
            </main>
        </div>
    );
}
