import React from 'react';
import { BookOpen, Building2, ExternalLink } from 'lucide-react';

// Hàm helper để parse màu dựa trên Rank
const getRankBadgeColor = (rank) => {
    if (!rank) return 'bg-gray-100 text-gray-800 border-gray-200';
    if (rank.includes('Q1')) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (rank.includes('Q2')) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (rank.includes('Q3')) return 'bg-orange-100 text-orange-800 border-orange-200';
    if (rank.includes('Q4')) return 'bg-red-100 text-red-800 border-red-200';
    return 'bg-blue-100 text-blue-800 border-blue-200';
};

export default function JournalCard({ journal }) {
    // SJR Rank là chuỗi text, ta tách thành badge nếu có (Mặc định API trả về "Q1", "Q1,Q2"...)
    const rankColor = getRankBadgeColor(journal.SJR_Rank);

    // Tạo link Search Google để tìm homepage của Journal
    const searchKeyword = `${journal.Title} ${journal.Publisher !== 'Unknown Publisher' ? journal.Publisher : ''} journal homepage`;
    const googleSearchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchKeyword)}`;

    return (
        <a 
            href={googleSearchUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="block h-full outline-none focus:ring-4 focus:ring-blue-500/20 rounded-2xl"
        >
            <div className="bg-white rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 hover:border-blue-200 border border-gray-100 p-5 transition-all duration-300 flex flex-col h-full group relative overflow-hidden">
                
                {/* Mũi tên out-link lúc hover */}
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity text-blue-500">
                    <ExternalLink size={18} />
                </div>

                {/* Header: Title & Rank */}
                <div className="flex justify-between items-start gap-4 mb-4 pr-6">
                    <h3 className="font-bold text-lg text-gray-900 leading-snug group-hover:text-blue-600 transition-colors">
                        {journal.Title}
                    </h3>
                </div>
                
                {/* Rank Badge xích xuống cho dễ nhìn thay vì nằm ngang chung dòng Title */}
                <div className="mb-4">
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold border shadow-sm ${rankColor}`}>
                        {journal.SJR_Rank !== "Unranked" ? journal.SJR_Rank : "N/A Rank"}
                    </span>
                </div>
                
                {/* Body: Meta info (Category, Publisher) */}
                <div className="mt-auto space-y-3 pt-4 border-t border-gray-50 flex-grow">
                    <div className="flex items-start gap-2 text-sm text-gray-600">
                        <BookOpen size={16} className="text-gray-400 mt-0.5 shrink-0" />
                        <p className="line-clamp-2" title={journal.Subject_Area_Category}>
                            {journal.Subject_Area_Category !== "Uncategorized" ? journal.Subject_Area_Category : "No Category"}
                        </p>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Building2 size={16} className="text-gray-400 shrink-0" />
                        <p className="truncate font-medium text-gray-700" title={journal.Publisher}>
                            {journal.Publisher}
                        </p>
                    </div>
                    
                    {/* ISSN Badge */}
                    {journal.ISSN && journal.ISSN !== "Unknown ISSN" && (
                        <div className="inline-block mt-2 px-2 py-1 bg-gray-50 text-gray-500 text-xs rounded border border-gray-100 font-mono">
                            ISSN: {journal.ISSN}
                        </div>
                    )}
                </div>
            </div>
        </a>
    );
}
