import axios from 'axios';

// Tạo config mặc định cho axios để dễ quản lý API
export const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api', 
    headers: {
        'Content-Type': 'application/json',
    }
});

// Hàm gọi API get journals
export const searchJournals = async (params) => {
    try {
        const { data } = await apiClient.get('/journals/search', { params });
        return data;
    } catch (error) {
        console.error("Error fetching journals:", error);
        throw error;
    }
};

// Hàm lấy Filter Options từ db
export const getFilterOptions = async () => {
    try {
        const { data } = await apiClient.get('/journals/filters');
        return data;
    } catch (error) {
        console.error("Error fetching defaults:", error);
        return { publishers: [], categories: [] };
    }
};
