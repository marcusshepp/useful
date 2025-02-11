```typescript
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-offer',
  templateUrl: './offer.component.html',
  styleUrls: ['./offer.component.css']
})
export class OfferComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

  offers = [
    {
      title: "Residential Property",
      text: "Our residential property management services provide comprehensive solutions for property owners and tenants",
      icon: "fa fa-home"
    },
    {
      title: "Commercial Property", 
      text: "Professional management services for office buildings, retail spaces and other commercial properties",
      icon: "fa fa-building"
    },
    {
      title: "Maintenance",
      text: "Regular maintenance and repairs to keep your property in excellent condition",
      icon: "fa fa-wrench"
    },
    {
      title: "Security",
      text: "24/7 security monitoring and access control systems to protect your property",
      icon: "fa fa-shield"
    }
  ];

}
```