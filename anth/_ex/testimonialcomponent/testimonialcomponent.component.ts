testimonial.component.ts:

```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-testimonial',
  templateUrl: './testimonial.component.html',
  styleUrls: ['./testimonial.component.css']
})
export class TestimonialComponent implements OnInit {
  testimonials = [
    {
      name: 'Client Name 1',
      position: 'Profession',
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis sed dapibus leo nec ornare diam sedasd commodo nibh ante facilisis bibendum dolor feugiat at.',
      image: 'assets/img/testimonials/01.jpg'
    },
    {
      name: 'Client Name 2',
      position: 'Profession',
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis sed dapibus leo nec ornare diam sedasd commodo nibh ante facilisis bibendum dolor feugiat at.',
      image: 'assets/img/testimonials/02.jpg'
    },
    {
      name: 'Client Name 3',
      position: 'Profession',
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis sed dapibus leo nec ornare diam sedasd commodo nibh ante facilisis bibendum dolor feugiat at.',
      image: 'assets/img/testimonials/03.jpg'
    },
    {
      name: 'Client Name 4',
      position: 'Profession',
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis sed dapibus leo nec ornare diam sedasd commodo nibh ante facilisis bibendum dolor feugiat at.',
      image: 'assets/img/testimonials/04.jpg'
    }
  ];

  constructor() { }

  ngOnInit(): void { }
}
```