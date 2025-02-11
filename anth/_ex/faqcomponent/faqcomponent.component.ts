```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-faq',
  templateUrl: './faq.component.html',
  styleUrls: ['./faq.component.css']
})
export class FaqComponent implements OnInit {

  faqs = [
    {
      question: "How does it work?",
      answer: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi aliquam neque id lorem tempus, at porttitor augue tincidunt. Sed eleifend metus sit amet tortor mattis, quis maximus lacus ornare.",
      isOpen: false
    },
    {
      question: "How much time does it take?", 
      answer: "Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec velit neque, auctor sit amet aliquam vel, ullamcorper sit amet ligula.",
      isOpen: false
    },
    {
      question: "What do I need to know?",
      answer: "Cras ultricies ligula sed magna dictum porta. Donec sollicitudin molestie malesuada. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.",
      isOpen: false
    },
    {
      question: "How do I get started?",
      answer: "Nulla quis lorem ut libero malesuada feugiat. Nulla quis lorem ut libero malesuada feugiat. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui.",
      isOpen: false
    },
    {
      question: "What are the features?",
      answer: "Curabitur aliquet quam id dui posuere blandit. Nulla quis lorem ut libero malesuada feugiat. Nulla quis lorem ut libero malesuada feugiat.",
      isOpen: false
    }
  ];

  constructor() { }

  ngOnInit(): void {
  }

  toggleFaq(faq: any): void {
    faq.isOpen = !faq.isOpen;
  }

}
```