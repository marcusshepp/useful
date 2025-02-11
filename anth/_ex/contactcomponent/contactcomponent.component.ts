contact.component.ts:

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent implements OnInit {
  contactForm: FormGroup;
  submitted = false;
  success = false;

  constructor(private formBuilder: FormBuilder) {
    this.contactForm = this.formBuilder.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      message: ['', Validators.required]
    });
  }

  ngOnInit(): void {
  }

  onSubmit() {
    this.submitted = true;

    if (this.contactForm.valid) {
      console.log(this.contactForm.value);
      this.success = true;
      this.contactForm.reset();
      this.submitted = false;
    }
  }

  get f() {
    return this.contactForm.controls;
  }
}
```