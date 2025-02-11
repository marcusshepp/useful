```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-populardishes',
  templateUrl: './populardishes.component.html',
  styleUrls: ['./populardishes.component.css']
})
export class PopulardishesComponent implements OnInit {

  dishes = [
    {
      name: 'Greek Salad',
      price: '$25.50',
      img: 'assets/images/greek-salad.png',
      rating: '4.9',
      ratingCount: '(1.4k Reviews)'
    },
    {
      name: 'Mozarella Sticks',
      price: '$13.00',
      img: 'assets/images/mozzarella.png', 
      rating: '4.7',
      ratingCount: '(2.1k Reviews)'
    },
    {
      name: 'Veg Spring Roll',
      price: '$15.00',
      img: 'assets/images/spring-rolls.png',
      rating: '4.8',
      ratingCount: '(1.2k Reviews)'
    },
    {
      name: 'Spicy Meatballs',
      price: '$19.00',
      img: 'assets/images/spicy-meatballs.png',
      rating: '4.9',
      ratingCount: '(1.8k Reviews)'
    }
  ];

  constructor() { }

  ngOnInit(): void {
  }

}
```