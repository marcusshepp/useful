brand.component.ts:

```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-brand',
  templateUrl: './brand.component.html',
  styleUrls: ['./brand.component.css']
})
export class BrandComponent implements OnInit {
  constructor() { }

  ngOnInit(): void {
  }
}
```

brand.module.ts:

```typescript
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BrandComponent } from './brand.component';

@NgModule({
  declarations: [
    BrandComponent
  ],
  imports: [
    CommonModule
  ],
  exports: [
    BrandComponent
  ]
})
export class BrandModule { }
```