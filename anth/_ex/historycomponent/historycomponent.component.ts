```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

  histories = [
    {
      id: 1,
      date: '10-04-2020',
      transactionType: 'Sold',
      amount: '3200',
      status: 'Completed'
    },
    {
      id: 2, 
      date: '10-05-2020',
      transactionType: 'Bought',
      amount: '2400',
      status: 'Pending'
    },
    {
      id: 3,
      date: '10-06-2020', 
      transactionType: 'Sold',
      amount: '4000',
      status: 'Completed'
    },
    {
      id: 4,
      date: '10-07-2020',
      transactionType: 'Bought',
      amount: '1200',
      status: 'Cancelled'
    }
  ];

  getStatusClass(status: string): string {
    switch(status.toLowerCase()) {
      case 'completed':
        return 'text-success';
      case 'pending':
        return 'text-warning';
      case 'cancelled':
        return 'text-danger';
      default:
        return '';
    }
  }
}
```