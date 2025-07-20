As a senior QA engineer, I've thoroughly reviewed the test suite design and identified the key areas for expansion. Below, you'll find the comprehensive automated test code for both your Java Spring Boot backend and Angular frontend, adhering to the specified frameworks, covering all augmented scenarios, edge cases, and addressing potential challenges.

I've made the following assumptions and added boilerplate/context code where necessary to make the tests runnable and comprehensive:
*   **Backend Entity/DTO/Service/Controller:** Assumed the existence of `Feedback`, `FeedbackDTO`, `FeedbackService`, `FeedbackRepository`, and `FeedbackController` classes within `com.example.feedback` package structure. I've provided minimal implementations of these to ensure the tests have a concrete target.
*   **Global Exception Handling:** Implemented a `GlobalExceptionHandler` to align with the expected JSON error responses for `400 Bad Request` and `500 Internal Server Error`, which are crucial for robust API testing.
*   **Frontend Component Structure:** Assumed standard Angular component structure with `ReactiveFormsModule` for form handling and `HttpClient` for API calls. Minimal HTML and TS for `FeedbackFormComponent` and `FeedbackService` are provided for context.
*   **Test Data:** Sample valid and invalid data is embedded within each test method for clarity.
*   **Challenges Addressed:**
    *   **Time-sensitive tests:** Used `java.time.Clock` with Mockito for fixed time in backend unit tests.
    *   **Asynchronous operations (Angular):** Utilized `fakeAsync` and `tick` in Angular unit tests to simulate async completion.
    *   **Database interactions:** Employed `Testcontainers` with PostgreSQL for backend integration tests to ensure real database behavior, along with `DynamicPropertySource` for configuration and `@Transactional` / `deleteAll` for state management.
    *   **HTML Sanitization:** Verified `HtmlUtils.htmlEscape` behavior in backend tests.

---

### **1. Backend Application Context (Assumed Files)**

These files are assumed to exist within your Spring Boot project structure and are necessary for the provided tests to run.

```java
filename: Feedback.java
directory: src/main/java/com/example/feedback/model
package com.example.feedback.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "feedback")
public class Feedback {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String subject; // Added for completeness, good practice for feedback

    @Column(name = "feedback_text", nullable = false, length = 2000)
    private String feedbackText;

    @Column(name = "user_email", length = 255)
    private String userEmail;

    @Column(name = "submission_date", nullable = false)
    private LocalDateTime submissionDate;

    // Constructors
    public Feedback() {}

    public Feedback(String subject, String feedbackText, String userEmail, LocalDateTime submissionDate) {
        this.subject = subject;
        this.feedbackText = feedbackText;
        this.userEmail = userEmail;
        this.submissionDate = submissionDate;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSubject() { return subject; }
    public void setSubject(String subject) { this.subject = subject; }
    public String getFeedbackText() { return feedbackText; }
    public void setFeedbackText(String feedbackText) { this.feedbackText = feedbackText; }
    public String getUserEmail() { return userEmail; }
    public void setUserEmail(String userEmail) { this.userEmail = userEmail; }
    public LocalDateTime getSubmissionDate() { return submissionDate; }
    public void setSubmissionDate(LocalDateTime submissionDate) { this.submissionDate = submissionDate; }

    @Override
    public String toString() {
        return "Feedback{" +
               "id=" + id +
               ", subject='" + subject + '\'' +
               ", feedbackText='" + feedbackText + '\'' +
               ", userEmail='" + userEmail + '\'' +
               ", submissionDate=" + submissionDate +
               '}';
    }
}
```

```java
filename: FeedbackDTO.java
directory: src/main/java/com/example/feedback/dto
package com.example.feedback.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class FeedbackDTO {

    @NotBlank(message = "Subject cannot be empty.")
    @Size(min = 3, max = 255, message = "Subject must be between 3 and 255 characters.")
    private String subject;

    @NotBlank(message = "Feedback text cannot be empty.")
    @Size(min = 10, max = 2000, message = "Feedback text must be between 10 and 2000 characters.")
    private String feedbackText;

    @Size(max = 255, message = "User email cannot exceed 255 characters.")
    @Email(message = "Invalid email format.", regexp = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,6}$")
    private String userEmail; // Optional field

    // Constructors
    public FeedbackDTO() {}

    public FeedbackDTO(String subject, String feedbackText, String userEmail) {
        this.subject = subject;
        this.feedbackText = feedbackText;
        this.userEmail = userEmail;
    }

    // Getters and Setters
    public String getFeedbackText() { return feedbackText; }
    public void setFeedbackText(String feedbackText) { this.feedbackText = feedbackText; }
    public String getUserEmail() { return userEmail; }
    public void setUserEmail(String userEmail) { this.userEmail = userEmail; }
    public String getSubject() { return subject; }
    public void setSubject(String subject) { this.subject = subject; }

    @Override
    public String toString() {
        return "FeedbackDTO{" +
               "feedbackText='" + feedbackText + '\'' +
               ", userEmail='" + userEmail + '\'' +
               ", subject='" + subject + '\'' +
               '}';
    }
}
```

```java
filename: FeedbackRepository.java
directory: src/main/java/com/example/feedback/repository
package com.example.feedback.repository;

import com.example.feedback.model.Feedback;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FeedbackRepository extends JpaRepository<Feedback, Long> {
}
```

```java
filename: FeedbackService.java
directory: src/main/java/com/example/feedback/service
package com.example.feedback.service;

import com.example.feedback.dto.FeedbackDTO;
import com.example.feedback.model.Feedback;
import com.example.feedback.repository.FeedbackRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.util.HtmlUtils;

import java.time.Clock;
import java.time.LocalDateTime;

@Service
public class FeedbackService {

    private final FeedbackRepository feedbackRepository;
    private final Clock clock; // Injected for testability of time-sensitive operations

    // Spring will automatically provide the default Clock if not explicitly mocked
    public FeedbackService(FeedbackRepository feedbackRepository, Clock clock) {
        this.feedbackRepository = feedbackRepository;
        this.clock = clock;
    }

    @Transactional
    public Feedback submitFeedback(FeedbackDTO feedbackDTO) {
        // Trim whitespace from feedback text and email before sanitization and persistence
        String trimmedFeedbackText = feedbackDTO.getFeedbackText() != null ? feedbackDTO.getFeedbackText().trim() : null;
        String trimmedUserEmail = feedbackDTO.getUserEmail() != null ? feedbackDTO.getUserEmail().trim() : null;
        String trimmedSubject = feedbackDTO.getSubject() != null ? feedbackDTO.getSubject().trim() : null;

        // HTML escape feedback text and subject to prevent XSS
        String sanitizedFeedbackText = (trimmedFeedbackText != null) ? HtmlUtils.htmlEscape(trimmedFeedbackText) : null;
        String sanitizedSubject = (trimmedSubject != null) ? HtmlUtils.htmlEscape(trimmedSubject) : null;


        // Handle empty email string as null for persistence (frontend might send empty string)
        if (trimmedUserEmail != null && trimmedUserEmail.isEmpty()) {
            trimmedUserEmail = null;
        }

        // Create Feedback entity
        Feedback feedback = new Feedback(
                sanitizedSubject,
                sanitizedFeedbackText,
                trimmedUserEmail,
                LocalDateTime.now(clock) // Use the injected clock for current time
        );

        return feedbackRepository.save(feedback);
    }
}
```

```java
filename: FeedbackController.java
directory: src/main/java/com/example/feedback/controller
package com.example.feedback.controller;

import com.example.feedback.dto.FeedbackDTO;
import com.example.feedback.model.Feedback;
import com.example.feedback.service.FeedbackService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/feedback")
public class FeedbackController {

    private final FeedbackService feedbackService;

    public FeedbackController(FeedbackService feedbackService) {
        this.feedbackService = feedbackService;
    }

    @PostMapping
    public ResponseEntity<Feedback> submitFeedback(@Valid @RequestBody FeedbackDTO feedbackDTO) {
        Feedback submittedFeedback = feedbackService.submitFeedback(feedbackDTO);
        return new ResponseEntity<>(submittedFeedback, HttpStatus.CREATED);
    }
}
```

```java
filename: GlobalExceptionHandler.java
directory: src/main/java/com/example/feedback/controller
package com.example.feedback.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.context.request.WebRequest;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(MethodArgumentNotValidException ex) {
        Map<String, String> errors = ex.getBindingResult().getFieldErrors().stream()
                .collect(Collectors.toMap(
                        fieldError -> fieldError.getField(),
                        fieldError -> fieldError.getDefaultMessage(),
                        (existingValue, newValue) -> existingValue // handle duplicate keys if any, though unlikely for field errors
                ));
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now().toString());
        response.put("status", HttpStatus.BAD_REQUEST.value());
        response.put("error", "Bad Request");
        response.put("message", "Validation failed");
        response.put("errors", errors);
        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ResponseEntity<Map<String, Object>> handleHttpMessageNotReadableException(HttpMessageNotReadableException ex) {
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now().toString());
        response.put("status", HttpStatus.BAD_REQUEST.value());
        response.put("error", "Bad Request");
        response.put("message", "Malformed JSON request");
        return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED)
    public ResponseEntity<Map<String, Object>> handleMethodNotSupportedException(HttpRequestMethodNotSupportedException ex) {
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now().toString());
        response.put("status", HttpStatus.METHOD_NOT_ALLOWED.value());
        response.put("error", "Method Not Allowed");
        response.put("message", String.format("Request method '%s' not supported. Supported methods are %s", ex.getMethod(), ex.getSupportedHttpMethods()));
        return new ResponseEntity<>(response, HttpStatus.METHOD_NOT_ALLOWED);
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ResponseEntity<Map<String, Object>> handleAllUncaughtException(Exception ex, WebRequest request) {
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now().toString());
        response.put("status", HttpStatus.INTERNAL_SERVER_ERROR.value());
        response.put("error", "Internal Server Error");
        response.put("message", "An unexpected error occurred.");
        // In a production environment, avoid exposing exception details
        // response.put("details", ex.getMessage());
        return new ResponseEntity<>(response, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

---

### **2. Frontend Application Context (Assumed Files)**

These files are assumed to exist within your Angular project structure and are necessary for the provided tests to run.

```typescript
filename: feedback.dto.ts
directory: src/app/feedback
export interface FeedbackDTO {
  subject: string;
  feedbackText: string;
  userEmail: string | null;
}
```

```typescript
filename: environment.ts
directory: src/environments
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8080' // Base URL for API calls
};
```

```typescript
filename: feedback.service.ts
directory: src/app/feedback
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { FeedbackDTO } from './feedback.dto';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class FeedbackService {
  private apiUrl = environment.apiUrl + '/api/feedback';

  constructor(private http: HttpClient) { }

  submitFeedback(feedback: FeedbackDTO): Observable<any> {
    return this.http.post(this.apiUrl, feedback);
  }
}
```

```typescript
filename: feedback-form.component.ts
directory: src/app/feedback/feedback-form
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FeedbackService } from '../feedback.service';
import { FeedbackDTO } from '../feedback.dto';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-feedback-form',
  templateUrl: './feedback-form.component.html',
  styleUrls: ['./feedback-form.component.css']
})
export class FeedbackFormComponent implements OnInit {
  feedbackForm!: FormGroup;
  submissionStatus: 'idle' | 'submitting' | 'success' | 'error' = 'idle';
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private feedbackService: FeedbackService
  ) { }

  ngOnInit(): void {
    this.feedbackForm = this.fb.group({
      subject: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(255)]],
      feedbackText: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(2000)]],
      userEmail: ['', [Validators.maxLength(255), Validators.email, Validators.pattern('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,6}$')]]
    });
  }

  onSubmit(): void {
    if (this.feedbackForm.valid) {
      this.submissionStatus = 'submitting';
      this.errorMessage = null;

      const feedbackData: FeedbackDTO = {
        subject: this.feedbackForm.value.subject,
        feedbackText: this.feedbackForm.value.feedbackText,
        userEmail: this.feedbackForm.value.userEmail === '' ? null : this.feedbackForm.value.userEmail // Handle empty string to null
      };

      this.feedbackService.submitFeedback(feedbackData).subscribe({
        next: (response) => {
          console.log('Feedback submitted successfully', response);
          this.submissionStatus = 'success';
          this.feedbackForm.reset();
          // Reset validation state for all controls after successful submission
          Object.keys(this.feedbackForm.controls).forEach(key => {
            this.feedbackForm.get(key)?.setErrors(null);
            this.feedbackForm.get(key)?.markAsUntouched();
            this.feedbackForm.get(key)?.markAsPristine();
          });
          setTimeout(() => this.submissionStatus = 'idle', 3000); // Reset status after some time
        },
        error: (errorResponse: HttpErrorResponse) => {
          console.error('Feedback submission failed', errorResponse);
          this.submissionStatus = 'error';
          if (errorResponse.status === 400 && errorResponse.error && errorResponse.error.errors) {
            // Server-side validation errors
            const backendErrors = errorResponse.error.errors;
            for (const field in backendErrors) {
              if (this.feedbackForm.controls[field]) {
                // Set specific error message for the field
                this.feedbackForm.controls[field].setErrors({ backendError: backendErrors[field] });
              }
            }
            this.errorMessage = 'Please correct the highlighted errors.';
          } else {
            this.errorMessage = 'Failed to submit feedback. Please try again later.';
          }
        }
      });
    } else {
      // Mark all fields as touched to display validation messages
      this.feedbackForm.markAllAsTouched();
      this.errorMessage = 'Please correct the form errors before submitting.';
    }
  }

  onCancel(): void {
    this.feedbackForm.reset();
    this.submissionStatus = 'idle';
    this.errorMessage = null;
    // Ensure all controls are untouches and pristine after reset
    Object.keys(this.feedbackForm.controls).forEach(key => {
      this.feedbackForm.get(key)?.setErrors(null);
      this.feedbackForm.get(key)?.markAsUntouched();
      this.feedbackForm.get(key)?.markAsPristine();
    });
  }

  // Helper to get form controls for easier access in template and tests
  get f() { return this.feedbackForm.controls; }
}
```

```html
filename: feedback-form.component.html
directory: src/app/feedback/feedback-form
<div class="feedback-container">
  <h2>Submit Your Feedback</h2>

  <form [formGroup]="feedbackForm" (ngSubmit)="onSubmit()">

    <div class="form-group">
      <label for="subject">Subject:</label>
      <input id="subject" type="text" formControlName="subject" [class.is-invalid]="f.subject.invalid && f.subject.touched">
      <div *ngIf="f.subject.invalid && f.subject.touched" class="invalid-feedback">
        <div *ngIf="f.subject.errors?.required">Subject is required.</div>
        <div *ngIf="f.subject.errors?.minlength">Subject must be at least 3 characters.</div>
        <div *ngIf="f.subject.errors?.maxlength">Subject cannot exceed 255 characters.</div>
        <div *ngIf="f.subject.errors?.backendError">{{ f.subject.errors?.backendError }}</div>
      </div>
    </div>

    <div class="form-group">
      <label for="feedbackText">Feedback:</label>
      <textarea id="feedbackText" formControlName="feedbackText" rows="5" [class.is-invalid]="f.feedbackText.invalid && f.feedbackText.touched"></textarea>
      <div *ngIf="f.feedbackText.invalid && f.feedbackText.touched" class="invalid-feedback">
        <div *ngIf="f.feedbackText.errors?.required">Feedback text is required.</div>
        <div *ngIf="f.feedbackText.errors?.minlength">Feedback text must be at least 10 characters.</div>
        <div *ngIf="f.feedbackText.errors?.maxlength">Feedback text cannot exceed 2000 characters.</div>
        <div *ngIf="f.feedbackText.errors?.backendError">{{ f.feedbackText.errors?.backendError }}</div>
      </div>
    </div>

    <div class="form-group">
      <label for="userEmail">Your Email (Optional):</label>
      <input id="userEmail" type="email" formControlName="userEmail" [class.is-invalid]="f.userEmail.invalid && f.userEmail.touched">
      <div *ngIf="f.userEmail.invalid && f.userEmail.touched" class="invalid-feedback">
        <div *ngIf="f.userEmail.errors?.email">Invalid email format.</div>
        <div *ngIf="f.userEmail.errors?.maxlength">User email cannot exceed 255 characters.</div>
        <div *ngIf="f.userEmail.errors?.backendError">{{ f.userEmail.errors?.backendError }}</div>
      </div>
    </div>

    <div class="form-actions">
      <button type="submit" [disabled]="feedbackForm.invalid || submissionStatus === 'submitting'">
        <ng-container *ngIf="submissionStatus === 'submitting'">Submitting...</ng-container>
        <ng-container *ngIf="submissionStatus !== 'submitting'">Submit Feedback</ng-container>
      </button>
      <button type="button" (click)="onCancel()" [disabled]="submissionStatus === 'submitting'">Cancel</button>
    </div>

    <div *ngIf="errorMessage" [class]="submissionStatus === 'error' ? 'alert alert-danger' : ''">
      {{ errorMessage }}
    </div>

    <div *ngIf="submissionStatus === 'success'" class="alert alert-success">
      Thank you for your feedback! It has been successfully submitted.
    </div>
  </form>
</div>
```
---

### **3. Generated Test Code**

#### **Backend Unit Tests (JUnit 5)**

```java
filename: FeedbackServiceTest.java
directory: src/test/java/com/example/feedback/service
package com.example.feedback.service;

import com.example.feedback.dto.FeedbackDTO;
import com.example.feedback.model.Feedback;
import com.example.feedback.repository.FeedbackRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.util.HtmlUtils;

import java.time.Clock;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class FeedbackServiceTest {

    @Mock
    private FeedbackRepository feedbackRepository;

    @Mock
    private Clock clock; // Mocking Clock for consistent LocalDateTime.now()

    @InjectMocks
    private FeedbackService feedbackService;

    // Fixed time for consistent testing of LocalDateTime
    private final Instant fixedInstant = Instant.parse("2023-01-01T10:00:00Z");
    private final ZoneId zoneId = ZoneId.of("UTC");
    private final LocalDateTime fixedLocalDateTime = LocalDateTime.ofInstant(fixedInstant, zoneId);

    @BeforeEach
    void setUp() {
        // Configure the mocked clock to return a fixed time
        when(clock.instant()).thenReturn(fixedInstant);
        when(clock.getZone()).thenReturn(zoneId);
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with feedback text exactly minimum length (10 characters).
     * Purpose: Verify that feedback with minimum length text is successfully saved.
     */
    @Test
    @DisplayName("shouldSaveFeedbackWithMinLengthText")
    void shouldSaveFeedbackWithMinLengthText() {
        String minLengthText = "0123456789"; // 10 characters
        FeedbackDTO feedbackDTO = new FeedbackDTO("Valid Subject", minLengthText, "test@example.com");
        Feedback expectedFeedback = new Feedback(feedbackDTO.getSubject(), minLengthText, "test@example.com", fixedLocalDateTime);
        expectedFeedback.setId(1L); // Simulate saved ID

        when(feedbackRepository.save(any(Feedback.class))).thenReturn(expectedFeedback);

        Feedback result = feedbackService.submitFeedback(feedbackDTO);

        assertThat(result).isNotNull();
        assertThat(result.getFeedbackText()).isEqualTo(HtmlUtils.htmlEscape(minLengthText)); // Service HTML escapes
        assertThat(result.getId()).isEqualTo(1L);
        verify(feedbackRepository, times(1)).save(any(Feedback.class));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with feedback text exactly maximum length (2000 characters).
     * Purpose: Verify that feedback with maximum length text is successfully saved.
     */
    @Test
    @DisplayName("shouldSaveFeedbackWithMaxLengthText")
    void shouldSaveFeedbackWithMaxLengthText() {
        String maxLengthText = "a".repeat(2000); // 2000 characters
        FeedbackDTO feedbackDTO = new FeedbackDTO("Valid Subject", maxLengthText, "longtext@example.com");
        Feedback expectedFeedback = new Feedback(feedbackDTO.getSubject(), maxLengthText, "longtext@example.com", fixedLocalDateTime);
        expectedFeedback.setId(2L);

        when(feedbackRepository.save(any(Feedback.class))).thenReturn(expectedFeedback);

        Feedback result = feedbackService.submitFeedback(feedbackDTO);

        assertThat(result).isNotNull();
        assertThat(result.getFeedbackText()).isEqualTo(HtmlUtils.htmlEscape(maxLengthText)); // Service HTML escapes
        verify(feedbackRepository, times(1)).save(any(Feedback.class));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with feedback text containing significant leading/trailing whitespace.
     * Purpose: Verify that feedback text is trimmed *before* sanitization and persistence.
     */
    @Test
    @DisplayName("shouldTrimWhitespaceFromFeedbackTextBeforeSanitization")
    void shouldTrimWhitespaceFromFeedbackTextBeforeSanitization() {
        String rawFeedbackText = "   Some feedback with spaces   ";
        String expectedTrimmedText = "Some feedback with spaces";
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", rawFeedbackText, "user@example.com");

        when(feedbackRepository.save(any(Feedback.class))).thenAnswer(invocation -> {
            Feedback feedback = invocation.getArgument(0);
            // In a real scenario, the service's HtmlUtils.htmlEscape will be called with the trimmed text.
            // Here, we just return the captured object as if it was saved.
            feedback.setId(3L);
            return feedback;
        });

        feedbackService.submitFeedback(feedbackDTO);

        // Capture the argument passed to save to verify trimming and sanitization
        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());

        Feedback capturedFeedback = feedbackCaptor.getValue();
        // Assert that the text was trimmed AND then HTML escaped
        assertThat(capturedFeedback.getFeedbackText()).isEqualTo(HtmlUtils.htmlEscape(expectedTrimmedText));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with `userEmail` containing significant leading/trailing whitespace.
     * Purpose: Verify that `userEmail` is trimmed *before* sanitization and persistence.
     */
    @Test
    @DisplayName("shouldTrimWhitespaceFromUserEmail")
    void shouldTrimWhitespaceFromUserEmail() {
        String rawEmail = "   user.name@example.com   ";
        String expectedTrimmedEmail = "user.name@example.com";
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", "Valid feedback text.", rawEmail);

        when(feedbackRepository.save(any(Feedback.class))).thenAnswer(invocation -> {
            Feedback feedback = invocation.getArgument(0);
            feedback.setId(4L);
            return feedback;
        });

        feedbackService.submitFeedback(feedbackDTO);

        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());

        Feedback capturedFeedback = feedbackCaptor.getValue();
        assertThat(capturedFeedback.getUserEmail()).isEqualTo(expectedTrimmedEmail);
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with empty `userEmail` string.
     * Purpose: Verify that an empty `userEmail` string is persisted as `null`.
     */
    @Test
    @DisplayName("shouldPersistEmptyEmailAsNull")
    void shouldPersistEmptyEmailAsNull() {
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", "Valid feedback text.", ""); // Empty string
        Feedback expectedFeedback = new Feedback("Subject", "Valid feedback text.", null, fixedLocalDateTime);
        expectedFeedback.setId(5L);

        when(feedbackRepository.save(any(Feedback.class))).thenReturn(expectedFeedback);

        Feedback result = feedbackService.submitFeedback(feedbackDTO);

        assertThat(result.getUserEmail()).isNull();
        // Verify that the saved object also had null email
        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());
        assertThat(feedbackCaptor.getValue().getUserEmail()).isNull();
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` where `feedbackRepository.save` encounters a transient database error.
     * Purpose: Verify that the exception is propagated (as `feedbackService` doesn't catch it),
     *          leading to a `500 Internal Server Error` at the controller level.
     */
    @Test
    @DisplayName("shouldPropagateRepositoryExceptionOnSaveFailure")
    void shouldPropagateRepositoryExceptionOnSaveFailure() {
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", "Valid feedback text.", "user@example.com");

        // Simulate a runtime exception from the repository (e.g., transient DB error)
        doThrow(new RuntimeException("Database connection lost")).when(feedbackRepository).save(any(Feedback.class));

        // Expect the exception to be thrown by the service method
        RuntimeException thrown = assertThrows(RuntimeException.class, () ->
                feedbackService.submitFeedback(feedbackDTO)
        );

        assertThat(thrown.getMessage()).isEqualTo("Database connection lost");
        verify(feedbackRepository, times(1)).save(any(Feedback.class));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with feedback text consisting solely of spaces (after trim, it becomes empty).
     * Purpose: Verify how the service handles input that becomes empty after trimming, and expects repository to fail due to non-nullable column.
     * Potential Challenge: This scenario usually is caught by `@NotBlank` at the controller. If it somehow bypasses,
     *                      the service will trim it to an empty string, HTML escape it (still empty), and attempt to save.
     *                      The database (configured for `nullable = false` on `feedback_text`) would then throw an error.
     */
    @Test
    @DisplayName("shouldPropagateErrorIfFeedbackTextBecomesEmptyAfterTrim")
    void shouldPropagateErrorIfFeedbackTextBecomesEmptyAfterTrim() {
        String feedbackTextWithSpaces = "      "; // Becomes empty string after trim
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", feedbackTextWithSpaces, "user@example.com");

        // Simulate behavior where saving an empty string to a non-nullable column throws an exception
        doThrow(new RuntimeException("Column 'feedback_text' cannot be empty")).when(feedbackRepository).save(any(Feedback.class));

        RuntimeException thrown = assertThrows(RuntimeException.class, () ->
                feedbackService.submitFeedback(feedbackDTO)
        );

        // Verify that HtmlUtils.htmlEscape was called with the trimmed empty string
        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());
        // HtmlUtils.htmlEscape("") results in ""
        assertThat(capturedFeedback.getFeedbackText()).isEqualTo("");

        assertThat(thrown.getMessage()).isEqualTo("Column 'feedback_text' cannot be empty");
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with an XSS payload in feedback text.
     * Purpose: Verify that feedback text is properly HTML-escaped to prevent XSS vulnerabilities.
     */
    @Test
    @DisplayName("shouldSanitizeFeedbackTextForXSS")
    void shouldSanitizeFeedbackTextForXSS() {
        String xssPayload = "<script>alert('XSS');</script>";
        String expectedSanitizedText = "&lt;script&gt;alert(&#39;XSS&#39;);&lt;/script&gt;";
        FeedbackDTO feedbackDTO = new FeedbackDTO("XSS Subject", xssPayload, "xss@example.com");

        when(feedbackRepository.save(any(Feedback.class))).thenAnswer(invocation -> {
            Feedback feedback = invocation.getArgument(0);
            feedback.setId(6L);
            return feedback;
        });

        feedbackService.submitFeedback(feedbackDTO);

        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());

        Feedback capturedFeedback = feedbackCaptor.getValue();
        assertThat(capturedFeedback.getFeedbackText()).isEqualTo(expectedSanitizedText);
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with special characters and Unicode characters in feedback text and subject.
     * Purpose: Verify handling and correct sanitization of various special characters and unicode.
     */
    @Test
    @DisplayName("shouldHandleSpecialAndUnicodeCharacters")
    void shouldHandleSpecialAndUnicodeCharacters() {
        String specialText = "Hello! 👋 This is some feedback with special characters: `~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?";
        String sanitizedSpecialText = HtmlUtils.htmlEscape(specialText);
        String specialSubject = "Subject with ÅÄÖéüñ characters";
        String sanitizedSpecialSubject = HtmlUtils.htmlEscape(specialSubject);
        
        FeedbackDTO feedbackDTO = new FeedbackDTO(specialSubject, specialText, "unicode@example.com");

        when(feedbackRepository.save(any(Feedback.class))).thenAnswer(invocation -> {
            Feedback feedback = invocation.getArgument(0);
            feedback.setId(7L);
            return feedback;
        });

        feedbackService.submitFeedback(feedbackDTO);

        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());

        Feedback capturedFeedback = feedbackCaptor.getValue();
        assertThat(capturedFeedback.getFeedbackText()).isEqualTo(sanitizedSpecialText);
        assertThat(capturedFeedback.getSubject()).isEqualTo(sanitizedSpecialSubject);
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: `submitFeedback` with `null` feedback text or subject.
     * Purpose: Confirm service behavior if `null` somehow reaches it, expecting repository save to fail due to `nullable = false` columns.
     * Potential Challenge: This should ideally be caught by `@NotBlank` at the controller/DTO level.
     */
    @Test
    @DisplayName("shouldFailIfFeedbackTextOrSubjectIsNull")
    void shouldFailIfFeedbackTextOrSubjectIsNull() {
        FeedbackDTO feedbackDTO = new FeedbackDTO(null, null, "test@example.com"); // Subject and feedbackText are null

        // HtmlUtils.htmlEscape(null) returns null.
        // This will result in saving a Feedback object with null feedbackText and subject,
        // which should trigger a constraint violation at the repository level given the @Column(nullable = false)
        doThrow(new RuntimeException("Column 'feedback_text' cannot be null")).when(feedbackRepository).save(any(Feedback.class));

        RuntimeException thrown = assertThrows(RuntimeException.class, () ->
                feedbackService.submitFeedback(feedbackDTO)
        );

        assertThat(thrown.getMessage()).isEqualTo("Column 'feedback_text' cannot be null");
        
        // Verify that the service tried to save a Feedback object with null feedbackText and subject
        ArgumentCaptor<Feedback> feedbackCaptor = ArgumentCaptor.forClass(Feedback.class);
        verify(feedbackRepository).save(feedbackCaptor.capture());
        assertThat(feedbackCaptor.getValue().getFeedbackText()).isNull();
        assertThat(feedbackCaptor.getValue().getSubject()).isNull();
    }
}
```

```java
filename: FeedbackControllerTest.java
directory: src/test/java/com/example/feedback/controller
package com.example.feedback.controller;

import com.example.feedback.dto.FeedbackDTO;
import com.example.feedback.model.Feedback;
import com.example.feedback.service.FeedbackService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.is;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = FeedbackController.class) // Tests only FeedbackController, mocks dependencies
// Ensure GlobalExceptionHandler is also picked up by @WebMvcTest
// Or specify it: @WebMvcTest(controllers = FeedbackController.class, includeFilters = @ComponentScan.Filter(type = FilterType.ASSIGNABLE_TYPE, classes = GlobalExceptionHandler.class))
class FeedbackControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean // Mock FeedbackService as it's a dependency of FeedbackController
    private FeedbackService feedbackService;

    /**
     * Test Category: Backend Unit Test
     * Scenario: Valid feedback with `userEmail` exactly maximum length (255 characters).
     * Purpose: Verify that feedback with a maximum length valid email is accepted.
     */
    @Test
    @DisplayName("shouldSubmitFeedbackWithMaxLengthEmail")
    void shouldSubmitFeedbackWithMaxLengthEmail() throws Exception {
        // Construct an email string that is exactly 255 characters long
        String maxLengthEmail = "a".repeat(240) + "@example.com";
        // Ensure it's exactly 255 if needed, or slightly less but still long and valid.
        if (maxLengthEmail.length() > 255) {
            maxLengthEmail = maxLengthEmail.substring(0, 255);
        }
        
        FeedbackDTO feedbackDTO = new FeedbackDTO("Valid Subject", "This is valid feedback text of sufficient length.", maxLengthEmail);
        Feedback mockFeedback = new Feedback(feedbackDTO.getSubject(), feedbackDTO.getFeedbackText(), feedbackDTO.getUserEmail(), LocalDateTime.now());
        mockFeedback.setId(1L);

        when(feedbackService.submitFeedback(any(FeedbackDTO.class))).thenReturn(mockFeedback);

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(feedbackDTO)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.feedbackText", is(feedbackDTO.getFeedbackText())))
                .andExpect(jsonPath("$.userEmail", is(feedbackDTO.getUserEmail())));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Valid feedback with `userEmail` exceeding maximum length (256+ characters).
     * Purpose: Verify that feedback with an email exceeding max length results in a Bad Request.
     */
    @Test
    @DisplayName("shouldReturnBadRequestForEmailExceedingMaxLength")
    void shouldReturnBadRequestForEmailExceedingMaxLength() throws Exception {
        String tooLongEmail = "a".repeat(250) + "@example.com.longdomain"; // Exceeds 255 characters
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", "This is valid feedback text of sufficient length.", tooLongEmail);

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(feedbackDTO)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors.userEmail", containsString("User email cannot exceed 255 characters.")));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Valid feedback with `userEmail` containing valid special characters (e.g., user.name+alias@sub.domain.co.uk).
     * Purpose: Verify that emails with common valid special characters are accepted.
     */
    @Test
    @DisplayName("shouldSubmitFeedbackWithSpecialCharacterEmail")
    void shouldSubmitFeedbackWithSpecialCharacterEmail() throws Exception {
        String specialEmail = "user.name+alias@sub.domain.co.uk";
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", "Valid feedback text.", specialEmail);
        Feedback mockFeedback = new Feedback(feedbackDTO.getSubject(), feedbackDTO.getFeedbackText(), feedbackDTO.getUserEmail(), LocalDateTime.now());
        mockFeedback.setId(2L);

        when(feedbackService.submitFeedback(any(FeedbackDTO.class))).thenReturn(mockFeedback);

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(feedbackDTO)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.userEmail", is(feedbackDTO.getUserEmail())));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Request body is malformed JSON (e.g., missing a quote, extra comma).
     * Purpose: Verify that malformed JSON requests result in a Bad Request (`HttpMessageNotReadableException`).
     */
    @Test
    @DisplayName("shouldReturnBadRequestForMalformedJson")
    void shouldReturnBadRequestForMalformedJson() throws Exception {
        String malformedJson = "{ \"subject\": \"Test\", \"feedbackText\": \"Valid feedback\", \"userEmail\": \"test@example.com\", "; // Missing closing brace

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(malformedJson))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message", containsString("Malformed JSON request")));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Request with `feedbackText` field explicitly `null` (not just an empty string).
     * Purpose: Verify that a `null` `feedbackText` field results in a Bad Request due to `@NotBlank` validation.
     */
    @Test
    @DisplayName("shouldReturnBadRequestForNullFeedbackText")
    void shouldReturnBadRequestForNullFeedbackText() throws Exception {
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", null, "test@example.com"); // feedbackText is null

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(feedbackDTO)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors.feedbackText", containsString("Feedback text cannot be empty.")));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Request to unsupported HTTP method (e.g., `GET /api/feedback`).
     * Purpose: Verify that requests to unsupported methods return `405 Method Not Allowed`.
     */
    @Test
    @DisplayName("shouldReturnMethodNotAllowedForUnsupportedHttpMethod")
    void shouldReturnMethodNotAllowedForUnsupportedHttpMethod() throws Exception {
        mockMvc.perform(get("/api/feedback"))
                .andExpect(status().isMethodNotAllowed());
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Backend service throws an internal error.
     * Purpose: Verify that internal service errors are handled by `GlobalExceptionHandler` and return `500 Internal Server Error`.
     */
    @Test
    @DisplayName("shouldReturnInternalServerErrorWhenServiceFails")
    void shouldReturnInternalServerErrorWhenServiceFails() throws Exception {
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", "Valid feedback text.", "test@example.com");

        // Simulate service throwing an exception
        doThrow(new RuntimeException("Simulated service failure")).when(feedbackService).submitFeedback(any(FeedbackDTO.class));

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(feedbackDTO)))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.message", containsString("An unexpected error occurred.")));
    }

    /**
     * Test Category: Backend Unit Test
     * Scenario: Request with `subject` field explicitly `null`.
     * Purpose: Verify that a `null` `subject` field results in a Bad Request due to `@NotBlank` validation.
     */
    @Test
    @DisplayName("shouldReturnBadRequestForNullSubject")
    void shouldReturnBadRequestForNullSubject() throws Exception {
        FeedbackDTO feedbackDTO = new FeedbackDTO(null, "Valid feedback text.", "test@example.com"); // Subject is null

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(feedbackDTO)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.errors.subject", containsString("Subject cannot be empty.")));
    }
}
```

#### **Frontend Unit Tests (Jasmine)**

```typescript
filename: feedback-form.component.spec.ts
directory: src/app/feedback/feedback-form
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { FeedbackFormComponent } from './feedback-form.component';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { FeedbackService } from '../feedback.service';
import { of, throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';

describe('FeedbackFormComponent', () => {
  let component: FeedbackFormComponent;
  let fixture: ComponentFixture<FeedbackFormComponent>;
  let feedbackServiceSpy: jasmine.SpyObj<FeedbackService>;
  let el: DebugElement;

  beforeEach(async () => {
    // Create a spy object for FeedbackService to control its behavior
    feedbackServiceSpy = jasmine.createSpyObj('FeedbackService', ['submitFeedback']);

    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, HttpClientTestingModule],
      declarations: [FeedbackFormComponent],
      providers: [
        { provide: FeedbackService, useValue: feedbackServiceSpy }
      ]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FeedbackFormComponent);
    component = fixture.componentInstance;
    el = fixture.debugElement; // For querying DOM elements
    fixture.detectChanges(); // Initialize the component and form
  });

  // Helper function to set form values and mark as touched
  function setFormValues(subject: string, feedbackText: string, userEmail: string | null = null) {
    component.feedbackForm.controls['subject'].setValue(subject);
    component.feedbackForm.controls['feedbackText'].setValue(feedbackText);
    if (userEmail !== null) {
      component.feedbackForm.controls['userEmail'].setValue(userEmail);
    }
    // Mark all controls as touched to ensure validation messages are displayed
    component.feedbackForm.markAllAsTouched();
    fixture.detectChanges();
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `feedbackText` field with exactly minimum length (10 chars).
   * Purpose: Verify that the form field `feedbackText` is valid at its minimum boundary.
   */
  @Test
  void shouldValidateFeedbackTextAtMinLength() {
    setFormValues('Valid Subject', '0123456789', 'test@example.com');
    expect(component.feedbackForm.controls['feedbackText'].valid).toBeTrue();
    // Ensure no error message is displayed
    expect(el.query(By.css('#feedbackText + .invalid-feedback'))).toBeNull();
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `feedbackText` field with exactly maximum length (2000 chars).
   * Purpose: Verify that the form field `feedbackText` is valid at its maximum boundary.
   */
  @Test
  void shouldValidateFeedbackTextAtMaxLength() {
    setFormValues('Valid Subject', 'a'.repeat(2000), 'test@example.com');
    expect(component.feedbackForm.controls['feedbackText'].valid).toBeTrue();
    // Ensure no error message is displayed
    expect(el.query(By.css('#feedbackText + .invalid-feedback'))).toBeNull();
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `feedbackText` field exceeding maximum length (2001+ characters typed).
   * Purpose: Verify that `maxlength` error appears for `feedbackText` when the input exceeds the limit.
   */
  @Test
  void shouldShowMaxLengthErrorForFeedbackText() {
    setFormValues('Valid Subject', 'a'.repeat(2001));
    expect(component.feedbackForm.controls['feedbackText'].invalid).toBeTrue();
    expect(component.f.feedbackText.errors?.['maxlength']).toBeTrue();

    const errorMsg = el.query(By.css('#feedbackText + .invalid-feedback div')).nativeElement.textContent;
    expect(errorMsg).toContain('Feedback text cannot exceed 2000 characters.');
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `userEmail` field with exactly maximum length (255 chars).
   * Purpose: Verify that the form field `userEmail` is valid at its maximum boundary.
   */
  @Test
  void shouldValidateUserEmailAtMaxLength() {
    const maxLengthEmail = 'verylongemailaddress' + 'a'.repeat(210) + '@example.com';
    setFormValues('Valid Subject', 'This is valid feedback.', maxLengthEmail);
    expect(component.feedbackForm.controls['userEmail'].valid).toBeTrue();
    expect(el.query(By.css('#userEmail + .invalid-feedback'))).toBeNull();
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `userEmail` field exceeding maximum length (256+ characters typed).
   * Purpose: Verify that `maxlength` error appears for `userEmail` when the input exceeds the limit.
   */
  @Test
  void shouldShowMaxLengthErrorForUserEmail() {
    const tooLongEmail = 'a'.repeat(250) + '@example.com.longdomain'; // Exceeds 255 chars
    setFormValues('Valid Subject', 'This is valid feedback.', tooLongEmail);
    expect(component.feedbackForm.controls['userEmail'].invalid).toBeTrue();
    expect(component.f.userEmail.errors?.['maxlength']).toBeTrue();

    const errorMsg = el.query(By.css('#userEmail + .invalid-feedback div')).nativeElement.textContent;
    expect(errorMsg).toContain('User email cannot exceed 255 characters.');
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: Successful submission then attempting to resubmit (button should be disabled while submitting, and form reset after success).
   * Purpose: Verify that the submit button state changes correctly, the form resets, and no double submission occurs.
   */
  @Test
  void shouldHandleSuccessfulSubmissionAndResetForm() {
    feedbackServiceSpy.submitFeedback.and.returnValue(of({ success: true }));

    setFormValues('Valid Subject', 'This is valid feedback text for submission test.', 'success@example.com');
    const submitButton: HTMLButtonElement = el.query(By.css('button[type="submit"]')).nativeElement;

    // Simulate clicking submit
    submitButton.click();
    fixture.detectChanges();

    // Verify 'submitting' state
    expect(component.submissionStatus).toBe('submitting');
    expect(submitButton.textContent).toContain('Submitting...');
    expect(submitButton.disabled).toBeTrue();
    expect(feedbackServiceSpy.submitFeedback).toHaveBeenCalledTimes(1);

    // Simulate async completion and wait for observables to complete
    fixture.whenStable().then(() => {
      fixture.detectChanges();
      // After service returns success
      expect(component.submissionStatus).toBe('success');
      expect(el.query(By.css('.alert-success'))).toBeTruthy();
      expect(el.query(By.css('.alert-success')).nativeElement.textContent).toContain('Thank you for your feedback!');

      // Verify form reset state
      expect(component.feedbackForm.pristine).toBeTrue();
      expect(component.feedbackForm.untouched).toBeTrue();
      expect(component.feedbackForm.value.subject).toBeNull(); // Form fields should be cleared
      expect(component.feedbackForm.value.feedbackText).toBeNull();
      expect(component.feedbackForm.value.userEmail).toBeNull();
      expect(submitButton.disabled).toBeFalse(); // Button should be re-enabled
      expect(submitButton.textContent).toContain('Submit Feedback'); // Button text should revert

      // Advance time for the setTimeout that resets submissionStatus to 'idle'
      fakeAsync(() => {
        tick(3000);
        fixture.detectChanges();
        expect(component.submissionStatus).toBe('idle');
        expect(el.query(By.css('.alert-success'))).toBeNull(); // Success message should be gone
      })();
    });
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: Backend returns a 400 validation error that the client-side didn't catch (e.g., a custom backend regex validation for email).
   * Purpose: Verify that `submissionStatus` is 'error', `errorMessage` updates, and the specific field shows the backend-provided error message.
   */
  @Test
  void shouldDisplayBackendValidationError() {
    const backendErrorResponse = new HttpErrorResponse({
      error: {
        errors: {
          userEmail: 'Email already registered. Please use a different one.'
        },
        message: 'Validation failed',
        status: 400,
        timestamp: '2023-01-01T12:00:00'
      },
      status: 400,
      statusText: 'Bad Request'
    });
    feedbackServiceSpy.submitFeedback.and.returnValue(throwError(() => backendErrorResponse));

    setFormValues('Subject', 'This feedback is valid client-side.', 'existing@example.com');
    component.onSubmit(); // Trigger submission
    fixture.detectChanges(); // Update component view

    expect(component.submissionStatus).toBe('error');
    expect(component.errorMessage).toBe('Please correct the highlighted errors.');

    // Verify the specific field error is set on the form control
    expect(component.f.userEmail.errors?.['backendError']).toBe('Email already registered. Please use a different one.');
    // Verify the specific error message is displayed in the DOM
    const emailErrorDiv = el.query(By.css('#userEmail + .invalid-feedback div[class*="backendError"]'));
    expect(emailErrorDiv).toBeTruthy();
    expect(emailErrorDiv.nativeElement.textContent).toContain('Email already registered. Please use a different one.');
    // Check general error message presence
    expect(el.query(By.css('.alert-danger'))).toBeTruthy();
    expect(el.query(By.css('.alert-danger')).nativeElement.textContent).toContain('Please correct the highlighted errors.');
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: Generic backend error display (e.g., 500 Internal Server Error).
   * Purpose: Verify that a generic error message is displayed and form fields remain populated.
   */
  @Test
  void shouldDisplayGenericBackendError() {
    const serverErrorResponse = new HttpErrorResponse({
      error: 'Internal Server Error',
      status: 500,
      statusText: 'Internal Server Error'
    });
    feedbackServiceSpy.submitFeedback.and.returnValue(throwError(() => serverErrorResponse));

    setFormValues('Subject', 'Valid feedback text for 500 error.', 'user@example.com');
    component.onSubmit(); // Trigger submission
    fixture.detectChanges(); // Update component view

    expect(component.submissionStatus).toBe('error');
    expect(component.errorMessage).toBe('Failed to submit feedback. Please try again later.');
    expect(el.query(By.css('.alert-danger'))).toBeTruthy();
    expect(el.query(By.css('.alert-danger')).nativeElement.textContent).toContain('Failed to submit feedback. Please try again later.');

    // Verify form fields are NOT cleared after a generic error
    expect(component.feedbackForm.value.subject).toBe('Subject');
    expect(component.feedbackForm.value.feedbackText).toBe('Valid feedback text for 500 error.');
    expect(component.feedbackForm.value.userEmail).toBe('user@example.com');
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: Form reset on Cancel click.
   * Purpose: Verify that all form fields are cleared, client-side validation messages are removed, and `submissionStatus` is reset.
   */
  @Test
  void shouldResetFormOnCancelClick() {
    // Populate form and put it in an invalid/error state
    setFormValues('Partial Subject', 'Partial feedback', 'partial@example.com');
    component.f.feedbackText.setErrors({ minlength: true }); // Manually set an error
    component.f.feedbackText.markAsTouched(); // Mark as touched to show error
    component.errorMessage = 'Form has errors.';
    component.submissionStatus = 'error';
    fixture.detectChanges();

    const cancelButton: HTMLButtonElement = el.query(By.css('button[type="button"]')).nativeElement;
    cancelButton.click(); // Simulate clicking the Cancel button
    fixture.detectChanges(); // Update component view

    // Verify form fields are cleared
    expect(component.feedbackForm.value.subject).toBeNull();
    expect(component.feedbackForm.value.feedbackText).toBeNull();
    expect(component.feedbackForm.value.userEmail).toBeNull();
    // Verify form state is reset
    expect(component.feedbackForm.pristine).toBeTrue();
    expect(component.feedbackForm.untouched).toBeTrue();
    expect(component.submissionStatus).toBe('idle');
    expect(component.errorMessage).toBeNull();

    // Verify no validation messages are visible in the DOM
    expect(el.query(By.css('.invalid-feedback'))).toBeNull();
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: Submit button state management (disabled when invalid, "Submitting..." during submission, enabled after).
   * Purpose: Verify that the submit button's disabled state and text change correctly based on form validity and submission status.
   */
  @Test
  void shouldManageSubmitButtonState() {
    const submitButton: HTMLButtonElement = el.query(By.css('button[type="submit"]')).nativeElement;

    // Initial state: Form is invalid, button should be disabled
    expect(component.feedbackForm.invalid).toBeTrue();
    expect(submitButton.disabled).toBeTrue();
    expect(submitButton.textContent).not.toContain('Submitting...');

    // Fill form with valid data: button should be enabled
    setFormValues('Valid Subject', 'This is valid feedback text of sufficient length.', 'valid@example.com');
    expect(component.feedbackForm.valid).toBeTrue();
    expect(submitButton.disabled).toBeFalse();
    expect(submitButton.textContent).not.toContain('Submitting...');

    // Simulate submission: button should show "Submitting..." and be disabled
    feedbackServiceSpy.submitFeedback.and.returnValue(of({ success: true }));
    submitButton.click();
    fixture.detectChanges();
    expect(component.submissionStatus).toBe('submitting');
    expect(submitButton.textContent).toContain('Submitting...');
    expect(submitButton.disabled).toBeTrue();

    // After submission completes (success): button should be re-enabled and revert text
    fixture.whenStable().then(() => {
      fixture.detectChanges();
      expect(component.submissionStatus).toBe('success');
      expect(submitButton.disabled).toBeFalse();
      expect(submitButton.textContent).toContain('Submit Feedback'); // Should revert to original text
    });
  }
});
```

```typescript
filename: feedback.service.spec.ts
directory: src/app/feedback
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { FeedbackService } from './feedback.service';
import { FeedbackDTO } from './feedback.dto';
import { environment } from '../../environments/environment';
import { HttpErrorResponse } from '@angular/common/http';

describe('FeedbackService', () => {
  let service: FeedbackService;
  let httpTestingController: HttpTestingController;
  const apiUrl = environment.apiUrl + '/api/feedback'; // Get the API URL from environment

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule], // Import HttpClientTestingModule to mock HttpClient
      providers: [FeedbackService]
    });
    service = TestBed.inject(FeedbackService);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  // After each test, verify that no outstanding requests are pending.
  afterEach(() => {
    httpTestingController.verify();
  });

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `submitFeedback` with `feedbackText` containing leading/trailing spaces.
   * Purpose: Verify that the `HttpClient` request payload for `feedbackText` still contains the spaces (trimming happens on backend).
   */
  @Test
  void shouldSendFeedbackTextWithLeadingTrailingSpaces() {
    const rawFeedbackText = "   Some feedback with spaces   ";
    const feedbackData: FeedbackDTO = {
      subject: "Test Subject",
      feedbackText: rawFeedbackText,
      userEmail: null
    };

    service.submitFeedback(feedbackData).subscribe(); // Subscribe to trigger the HTTP request

    const req = httpTestingController.expectOne(apiUrl); // Expect one request to the API URL
    expect(req.request.method).toBe('POST');
    expect(req.request.body.feedbackText).toBe(rawFeedbackText); // Verify raw text is sent in the request body
    req.flush({}); // Respond to the request to complete the observable
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `submitFeedback` with `userEmail` containing leading/trailing spaces.
   * Purpose: Verify that the `HttpClient` request payload for `userEmail` still contains the spaces (trimming happens on backend).
   */
  @Test
  void shouldSendUserEmailWithLeadingTrailingSpaces() {
    const rawUserEmail = "   user@example.com   ";
    const feedbackData: FeedbackDTO = {
      subject: "Test Subject",
      feedbackText: "Valid feedback.",
      userEmail: rawUserEmail
    };

    service.submitFeedback(feedbackData).subscribe();

    const req = httpTestingController.expectOne(apiUrl);
    expect(req.request.method).toBe('POST');
    expect(req.request.body.userEmail).toBe(rawUserEmail); // Verify raw email is sent in the request body
    req.flush({});
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `submitFeedback` when the backend returns a non-2xx status code (e.g., 400, 500).
   * Purpose: Verify that the `Observable` returned by `submitFeedback` emits an error when the backend responds with an error status.
   */
  @Test
  void shouldEmitErrorOnHttpErrorResponse() {
    const feedbackData: FeedbackDTO = {
      subject: "Test Subject",
      feedbackText: "Valid feedback.",
      userEmail: "test@example.com"
    };
    const mockError = new HttpErrorResponse({
      error: 'Backend Error',
      status: 500,
      statusText: 'Internal Server Error'
    });

    service.submitFeedback(feedbackData).subscribe({
      next: () => fail('should have failed with the 500 error'), // Should not call next
      error: (error) => {
        expect(error).toBe(mockError); // Assert the error object itself
        expect(error.status).toBe(500);
        expect(error.statusText).toBe('Internal Server Error');
      }
    });

    const req = httpTestingController.expectOne(apiUrl);
    req.flush('Something went wrong', mockError); // Use flush with error object to simulate an error response
  }

  /**
   * Test Category: Frontend Unit Test
   * Scenario: `submitFeedback` sends a POST request with null email if not provided (i.e., component sets it to null for empty string).
   * Purpose: Verify that `userEmail` is sent as `null` in the HTTP request payload when the DTO's `userEmail` property is `null`.
   */
  @Test
  void shouldSendPostRequestWithNullEmailIfNullProvidedInDTO() {
    const feedbackData: FeedbackDTO = {
      subject: "Test Subject",
      feedbackText: 'This is some feedback.',
      userEmail: null // The component logic is expected to convert "" to null here
    };

    service.submitFeedback(feedbackData).subscribe(response => {
      expect(response).toEqual({}); // Expect a successful empty response
    });

    const req = httpTestingController.expectOne(apiUrl);
    expect(req.request.method).toBe('POST');
    expect(req.request.body.feedbackText).toBe('This is some feedback.');
    expect(req.request.body.userEmail).toBeNull(); // Assert that userEmail is null in the request body
    req.flush({});
  }
});
```

#### **Integration Tests (Backend) with Spring Test and Testcontainers**

```java
filename: FeedbackIntegrationTest.java
directory: src/test/java/com/example/feedback
package com.example.feedback;

import com.example.feedback.dto.FeedbackDTO;
import com.example.feedback.model.Feedback;
import com.example.feedback.repository.FeedbackRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.util.HtmlUtils;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

// Annotate with @SpringBootTest to load the full Spring application context
// Use WebEnvironment.RANDOM_PORT to start the server on a random available port
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
// Enable Testcontainers integration for JUnit 5
@Testcontainers
class FeedbackIntegrationTest {

    @LocalServerPort
    private int port; // Injects the dynamically assigned port

    @Autowired
    private TestRestTemplate restTemplate; // Used to make HTTP requests to the running app

    @Autowired
    private FeedbackRepository feedbackRepository; // To verify database state directly

    // Define the PostgreSQL container
    // Using a specific tag like "postgres:13-alpine" is good practice for reproducibility
    @Container
    public static PostgreSQLContainer<?> postgresContainer = new PostgreSQLContainer<>("postgres:13-alpine")
            .withDatabaseName("testdb")
            .withUsername("testuser")
            .withPassword("testpass");

    // Dynamically configure datasource properties to connect to the Testcontainers database
    @DynamicPropertySource
    static void setDatasourceProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgresContainer::getJdbcUrl);
        registry.add("spring.datasource.username", postgresContainer::getUsername);
        registry.add("spring.datasource.password", postgresContainer::getPassword);
        // "create-drop" ensures the schema is created and dropped for each test run, providing a clean state
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");
        registry.add("spring.jpa.properties.hibernate.default_schema", () -> "public"); // Explicitly set default schema
        registry.add("spring.jpa.show-sql", () -> "true"); // Show SQL in logs for debugging
        registry.add("spring.jpa.properties.hibernate.format_sql", () -> "true"); // Format SQL for readability
    }

    @BeforeEach
    @Transactional // Ensure operations within beforeEach (like deleteAll) are transactional
    void setUp() {
        // Cleaning up the database before each test to ensure test isolation.
        // `create-drop` from DynamicPropertySource should handle schema creation.
        // `deleteAll` ensures any data from previous tests is removed.
        feedbackRepository.deleteAll();
    }


    /**
     * Test Category: Backend Integration Test
     * Scenario: Full Stack Happy Path Submission.
     * Purpose: Verify that a valid feedback submission successfully goes through the entire stack
     *          (Controller -> Service -> Repository) and is persisted in the database.
     */
    @Test
    @DisplayName("shouldSubmitValidFeedbackAndPersistToDB")
    void shouldSubmitValidFeedbackAndPersistToDB() {
        String url = "http://localhost:" + port + "/api/feedback";
        FeedbackDTO feedbackDTO = new FeedbackDTO("Integration Test Subject", "This is a comprehensive feedback text for an integration test.", "integration@example.com");

        // Act: Send POST request to the running application
        ResponseEntity<Feedback> response = restTemplate.postForEntity(url, feedbackDTO, Feedback.class);

        // Assert: HTTP 201 Created status
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertNotNull(response.getBody());
        assertThat(response.getBody().getId()).isNotNull();
        // The response body reflects the entity returned by the service, which has been HTML escaped
        assertThat(response.getBody().getFeedbackText()).isEqualTo(HtmlUtils.htmlEscape(feedbackDTO.getFeedbackText()));
        assertThat(response.getBody().getSubject()).isEqualTo(HtmlUtils.htmlEscape(feedbackDTO.getSubject()));
        assertThat(response.getBody().getUserEmail()).isEqualTo(feedbackDTO.getUserEmail());
        assertNotNull(response.getBody().getSubmissionDate());

        // Assert: Directly query the database to confirm the entry exists and matches
        List<Feedback> feedbacksInDb = feedbackRepository.findAll();
        assertThat(feedbacksInDb).hasSize(1);
        Feedback persistedFeedback = feedbacksInDb.get(0);
        assertThat(persistedFeedback.getSubject()).isEqualTo(HtmlUtils.htmlEscape(feedbackDTO.getSubject()));
        assertThat(persistedFeedback.getFeedbackText()).isEqualTo(HtmlUtils.htmlEscape(feedbackDTO.getFeedbackText()));
        assertThat(persistedFeedback.getUserEmail()).isEqualTo(feedbackDTO.getUserEmail());
        assertThat(persistedFeedback.getId()).isEqualTo(response.getBody().getId());
        // Check submission date is within a reasonable window (e.g., last 1 minute)
        assertTrue(persistedFeedback.getSubmissionDate().isAfter(LocalDateTime.now().minus(1, ChronoUnit.MINUTES)) &&
                   persistedFeedback.getSubmissionDate().isBefore(LocalDateTime.now().plus(1, ChronoUnit.MINUTES)));
    }

    /**
     * Test Category: Backend Integration Test
     * Scenario: Submission without Email (Optional Field Handling).
     * Purpose: Verify that feedback submitted with an empty/null `userEmail` is correctly handled and persisted as `null` in the database.
     */
    @Test
    @DisplayName("shouldSubmitFeedbackWithoutEmailAndPersistNull")
    void shouldSubmitFeedbackWithoutEmailAndPersistNull() {
        String url = "http://localhost:" + port + "/api/feedback";
        FeedbackDTO feedbackDTO = new FeedbackDTO("No Email Subject", "Another valid feedback text.", ""); // Empty string for email

        // Act
        ResponseEntity<Feedback> response = restTemplate.postForEntity(url, feedbackDTO, Feedback.class);

        // Assert HTTP status
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertNotNull(response.getBody());
        assertThat(response.getBody().getId()).isNotNull();
        assertThat(response.getBody().getUserEmail()).isNull(); // Should be null in response as service converts "" to null

        // Assert DB state: `userEmail` should be `NULL`
        List<Feedback> feedbacksInDb = feedbackRepository.findAll();
        assertThat(feedbacksInDb).hasSize(1);
        Feedback persistedFeedback = feedbacksInDb.get(0);
        assertThat(persistedFeedback.getUserEmail()).isNull(); // Should be null in DB
    }

    /**
     * Test Category: Backend Integration Test
     * Scenario: Input Sanitization Verification.
     * Purpose: Verify that feedback text containing XSS payloads is properly HTML-escaped by the service before persistence.
     */
    @Test
    @DisplayName("shouldSanitizeXSSPayloadInFeedbackText")
    void shouldSanitizeXSSPayloadInFeedbackText() {
        String url = "http://localhost:" + port + "/api/feedback";
        String xssPayload = "<script>alert('XSS');</script>";
        String expectedSanitizedText = HtmlUtils.htmlEscape(xssPayload); // The expected HTML-escaped string
        FeedbackDTO feedbackDTO = new FeedbackDTO("XSS Test Subject", xssPayload, "xss@example.com");

        // Act
        ResponseEntity<Feedback> response = restTemplate.postForEntity(url, feedbackDTO, Feedback.class);

        // Assert HTTP status (should still be 201 if sanitization works)
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertNotNull(response.getBody());
        assertThat(response.getBody().getFeedbackText()).isEqualTo(expectedSanitizedText); // Response reflects sanitized text

        // Assert DB state: retrieved feedback should have the *sanitized* text
        List<Feedback> feedbacksInDb = feedbackRepository.findAll();
        assertThat(feedbacksInDb).hasSize(1);
        Feedback persistedFeedback = feedbacksInDb.get(0);
        assertThat(persistedFeedback.getFeedbackText()).isEqualTo(expectedSanitizedText);
    }

    /**
     * Test Category: Backend Integration Test
     * Scenario: Backend Validation Triggered by Boundary Value (too short feedbackText).
     * Purpose: Verify that client-side invalid data (if not caught) is ultimately caught by backend `@Valid` annotation
     *          and returns a `400 Bad Request` without persisting data.
     */
    @Test
    @DisplayName("shouldReturnBadRequestForTooShortFeedbackText")
    void shouldReturnBadRequestForTooShortFeedbackText() {
        String url = "http://localhost:" + port + "/api/feedback";
        String shortFeedbackText = "Short"; // 5 characters, min is 10 as per DTO validation
        FeedbackDTO feedbackDTO = new FeedbackDTO("Subject", shortFeedbackText, "invalid@example.com");

        // Act
        ResponseEntity<String> response = restTemplate.postForEntity(url, feedbackDTO, String.class);

        // Assert HTTP status 400 Bad Request
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        // Verify response body contains validation error message from GlobalExceptionHandler
        assertThat(response.getBody()).contains("Feedback text must be between 10 and 2000 characters.");

        // Assert DB state: no new records should be in the database
        List<Feedback> feedbacksInDb = feedbackRepository.findAll();
        assertThat(feedbacksInDb).isEmpty();
    }

    /**
     * Test Category: Backend Integration Test
     * Scenario: Database Constraint Violation (Hypothetical - via a null mandatory field).
     * Purpose: Verify that if a mandatory field, like `subject`, is sent as `null` and
     *          it also has a `nullable=false` DB constraint, Spring's validation catches it (`400 Bad Request`).
     * Challenge Addressed: `DataIntegrityViolationException` is often tricky to trigger directly in tests due
     *                      to `@Valid` catching issues earlier. This test confirms the validation chain works.
     */
    @Test
    @DisplayName("shouldReturnBadRequestForNullSubjectDueToValidation")
    void shouldReturnBadRequestForNullSubjectDueToValidation() {
        String url = "http://localhost:" + port + "/api/feedback";
        // Send a DTO with a null subject, which is @NotBlank and nullable=false in DB
        FeedbackDTO feedbackDTO = new FeedbackDTO(null, "Valid feedback text.", "test@example.com");

        // Act
        ResponseEntity<String> response = restTemplate.postForEntity(url, feedbackDTO, String.class);

        // Assert HTTP status 400 Bad Request due to @NotBlank validation on the DTO
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody()).contains("Subject cannot be empty."); // From @NotBlank message
        // Assert DB state: no new records should be in the database
        assertThat(feedbackRepository.findAll()).isEmpty();
    }


    /**
     * Test Category: Backend Integration Test
     * Scenario: Concurrent Valid Submissions (Limited Scale).
     * Purpose: Verify system handles multiple simultaneous requests correctly without data loss or conflicts,
     *          and that all submissions are persisted uniquely.
     */
    @Test
    @DisplayName("shouldHandleConcurrentValidSubmissions")
    void shouldHandleConcurrentValidSubmissions() throws Exception {
        String url = "http://localhost:" + port + "/api/feedback";
        int numberOfSubmissions = 10; // A small, controlled number for integration test concurrency
        ExecutorService executorService = Executors.newFixedThreadPool(numberOfSubmissions);

        List<Future<ResponseEntity<Feedback>>> futures = IntStream.range(0, numberOfSubmissions)
                .mapToObj(i -> executorService.submit(() -> {
                    FeedbackDTO feedbackDTO = new FeedbackDTO(
                        "Concurrent Subject " + i,
                        "Feedback " + i + ": This is valid feedback for concurrent test. " + "x".repeat(100),
                        "user" + i + "@example.com"
                    );
                    return restTemplate.postForEntity(url, feedbackDTO, Feedback.class);
                }))
                .collect(Collectors.toList());

        // Wait for all submissions to complete and assert their individual results
        for (Future<ResponseEntity<Feedback>> future : futures) {
            ResponseEntity<Feedback> response = future.get(); // .get() blocks until task completes or throws exception
            assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
            assertNotNull(response.getBody());
            assertThat(response.getBody().getId()).isNotNull();
        }

        // Shut down the executor and wait for tasks to finish
        executorService.shutdown();
        assertTrue(executorService.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS), "Executor did not terminate in time");


        // Assert: Verify all submissions are in the database
        List<Feedback> feedbacksInDb = feedbackRepository.findAll();
        assertThat(feedbacksInDb).hasSize(numberOfSubmissions);
        // Additional checks: ensure unique data where expected, correct values.
        long distinctEmails = feedbacksInDb.stream().map(Feedback::getUserEmail).distinct().count();
        assertThat(distinctEmails).isEqualTo(numberOfSubmissions); // All emails should be distinct if they were generated uniquely
        long distinctFeedbackTexts = feedbacksInDb.stream().map(Feedback::getFeedbackText).distinct().count();
        assertThat(distinctFeedbackTexts).isEqualTo(numberOfSubmissions); // All feedback texts should be distinct
    }

    /**
     * Test Category: Backend Integration Test
     * Scenario: Request body is malformed JSON.
     * Purpose: Verify that malformed JSON requests are rejected by the API with a `400 Bad Request` status.
     */
    @Test
    @DisplayName("shouldReturnBadRequestForMalformedJsonIntegration")
    void shouldReturnBadRequestForMalformedJsonIntegration() {
        String url = "http://localhost:" + port + "/api/feedback";
        // Malformed JSON: missing a closing quote and brace
        String malformedJson = "{ \"subject\": \"Test\", \"feedbackText\": \"Valid feedback\", \"userEmail\": \"test@example.com\", ";

        // Using postForEntity with a String content type to send raw malformed JSON
        ResponseEntity<String> response = restTemplate.postForEntity(url, malformedJson, String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(response.getBody()).contains("Malformed JSON request"); // As handled by GlobalExceptionHandler
    }
}
```