header.component.ts:
```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  isNavbarCollapsed = true;

  toggleNavbar() {
    this.isNavbarCollapsed = !this.isNavbarCollapsed;
  }
}
```

header.component.html:
```html
<header class="header-section">
  <nav class="navbar navbar-expand-lg navbar-light">
    <div class="container">
      <a class="navbar-brand" routerLink="/">Logo</a>
      <button class="navbar-toggler" type="button" (click)="toggleNavbar()">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" [ngClass]="{'show': !isNavbarCollapsed}">
        <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}">Home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" routerLink="/about" routerLinkActive="active">About</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" routerLink="/services" routerLinkActive="active">Services</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" routerLink="/contact" routerLinkActive="active">Contact</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</header>
```

header.component.css:
```css
.header-section {
  background-color: #ffffff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
}

.navbar {
  padding: 15px 0;
}

.navbar-brand {
  font-weight: bold;
  font-size: 24px;
  color: #333;
}

.nav-link {
  color: #333;
  font-weight: 500;
  margin: 0 10px;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #007bff;
}

.nav-link.active {
  color: #007bff;
}

.navbar-toggler {
  border: none;
  padding: 0;
}

.navbar-toggler:focus {
  outline: none;
}

@media (max-width: 991px) {
  .navbar-nav {
    padding-top: 15px;
  }
  
  .nav-link {
    padding: 10px 0;
  }
}
```