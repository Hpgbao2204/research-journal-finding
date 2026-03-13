import { useState, useEffect } from 'react';

/**
 * Custom hook giúp delay việc cập nhật giá trị (Debounce).
 * Hữu ích cho việc gõ ô search xong mới bắt đầu gọi API.
 */
export default function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        // Hủy timeout nếu value thay đổi liên tục trước khi hết delay
        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]);

    return debouncedValue;
}
