food-menu.component.ts:

```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-food-menu',
  templateUrl: './food-menu.component.html',
  styleUrls: ['./food-menu.component.css']
})
export class FoodMenuComponent implements OnInit {
  
  menu = [
    {
      category: 'Starters',
      items: [
        { name: 'Bruschetta', price: 8.99, description: 'Toasted bread with tomatoes, garlic, and basil' },
        { name: 'Calamari', price: 10.99, description: 'Crispy fried squid with marinara sauce' },
        { name: 'Soup of the Day', price: 6.99, description: 'Fresh homemade soup' }
      ]
    },
    {
      category: 'Main Course',
      items: [
        { name: 'Grilled Salmon', price: 24.99, description: 'Fresh salmon with seasonal vegetables' },
        { name: 'Beef Tenderloin', price: 29.99, description: 'Prime cut with mushroom sauce' },
        { name: 'Pasta Primavera', price: 18.99, description: 'Fresh vegetables in cream sauce' }
      ]
    },
    {
      category: 'Desserts',
      items: [
        { name: 'Tiramisu', price: 7.99, description: 'Classic Italian dessert' },
        { name: 'Chocolate Cake', price: 6.99, description: 'Rich chocolate layer cake' },
        { name: 'Ice Cream', price: 5.99, description: 'Variety of flavors' }
      ]
    }
  ];

  constructor() { }

  ngOnInit(): void { }
}
```