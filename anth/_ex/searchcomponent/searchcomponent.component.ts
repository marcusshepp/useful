```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-search',
  template: `
    <form class="d-flex">
      <input 
        class="form-control me-2" 
        type="search" 
        [(ngModel)]="searchTerm"
        name="search"
        placeholder="Search" 
        aria-label="Search">
      <button class="btn btn-outline-success" type="submit" (click)="onSearch()">Search</button>
    </form>
  `
})
export class SearchComponent implements OnInit {
  searchTerm: string = '';

  constructor() { }

  ngOnInit(): void {
  }

  onSearch(): void {
    console.log('Searching for:', this.searchTerm);
  }
}
```