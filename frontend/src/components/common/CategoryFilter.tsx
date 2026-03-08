import { CATEGORIES } from '../../constants/categories';

interface CategoryFilterProps {
    selectedCategory: string; // 선택된 카테고리
    onSelectCategory: (category: string) => void;
}

const CategoryFilter = ({ selectedCategory, onSelectCategory }: CategoryFilterProps) => {
    return (
        <div className={`flex gap-2 overflow-x-auto pb-1 scrollbar-hide px-1`}>
            {CATEGORIES.map((cat) => (
                <button
                    key={cat.id}
                    onClick={() => onSelectCategory(cat.id)}
                    className={`
            flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-normal shadow-sm border transition-all whitespace-nowrap
            ${selectedCategory === cat.id
                            ? 'bg-[#42BCEB] text-white border-[#42BCEB]'
                            : 'bg-white text-black border-[#42BCEB]'}
          `}
                >
                    {cat.icon && (
                        <svg
                            width="14"
                            height="14"
                            viewBox={(cat as any).viewBox || "0 0 24 24"}
                            fill="currentColor"
                            className={selectedCategory === cat.id ? "text-white" : "text-[#42BCEB]"}
                        >
                            {cat.icon}
                        </svg>
                    )}
                    {cat.name}
                </button>
            ))}
        </div>
    );
};

export default CategoryFilter;
