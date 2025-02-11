
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-h',
  template: '<h1>{{title}}</h1>',
  styles: []
})
export class HComponent implements OnInit {
  title = 'Welcome to My App';

  constructor() { }

  ngOnInit(): void {
  }
}