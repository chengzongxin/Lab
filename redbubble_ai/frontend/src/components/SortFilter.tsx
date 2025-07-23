import React from 'react';
import './SortFilter.css';

export type SortOption = 'default' | 'score-high' | 'score-low' | 'title';

interface Props {
  currentSort: SortOption;
  onSortChange: (sort: SortOption) => void;
}

const SortFilter: React.FC<Props> = ({ currentSort, onSortChange }) => {
  return (
    <div className="sort-container">
      <div className="sort-label">排序方式：</div>
      <select 
        value={currentSort} 
        onChange={(e) => onSortChange(e.target.value as SortOption)}
        className="sort-select"
      >
        <option value="default">默认排序</option>
        <option value="score-high">评分从高到低</option>
        <option value="score-low">评分从低到高</option>
        <option value="title">按名称排序</option>
      </select>
    </div>
  );
};

export default SortFilter; 