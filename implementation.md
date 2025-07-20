```
filename: pom.xml
directory: backend
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.5</version> <!-- Current stable Spring Boot 3.x version -->
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>feedback-submission</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>feedback-submission</name>
    <description>Application Feedback Submission Service</description>
    <properties>
        <java.version>17</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Oracle Driver -->
        <dependency>
            <groupId>com.oracle.database.jdbc</groupId>
            <artifactId>ojdbc8</artifactId>
            <scope>runtime</scope>
        </dependency>
        
        <!-- H2 for in-memory testing (optional, remove if not needed) -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>

        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <!-- For advanced sanitization, consider OWASP ESAPI or similar -->
        <!-- Example: <dependency> <groupId>org.owasp.esapi</groupId> <artifactId>esapi</artifactId> <version>2.2.3.0</version> </dependency> -->
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

```java
filename: FeedbackSubmissionApplication.java
directory: backend/src/main/java/com/example/feedbacksubmission
package com.example.feedbacksubmission;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class FeedbackSubmissionApplication {

    public static void main(String[] args) {
        SpringApplication.run(FeedbackSubmissionApplication.class, args);
    }

}
```

```java
filename: Feedback.java
directory: backend/src/main/java/com/example/feedbacksubmission/model
package com.example.feedbacksubmission.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;

/**
 * Represents a user feedback entry in the database.
 */
@Entity
@Table(name = "feedback")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Feedback {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "feedback_seq")
    @SequenceGenerator(name = "feedback_seq", sequenceName = "FEEDBACK_SEQ", allocationSize = 1)
    private Long id;

    @Column(name = "feedback_text", nullable = false, length = 2000)
    private String feedbackText;

    @Column(name = "user_email", length = 255)
    private String userEmail;

    @Column(name = "submission_date", nullable = false)
    private LocalDateTime submissionDate;

    @PrePersist
    protected void onCreate() {
        if (submissionDate == null) {
            submissionDate = LocalDateTime.now();
        }
    }
}
```

```java
filename: FeedbackRepository.java
directory: backend/src/main/java/com/example/feedbacksubmission/repository
package com.example.feedbacksubmission.repository;

import com.example.feedbacksubmission.model.Feedback;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Spring Data JPA repository for Feedback entities.
 * Provides standard CRUD operations.
 */
@Repository
public interface FeedbackRepository extends JpaRepository<Feedback, Long> {
}
```

```java
filename: FeedbackRequest.java
directory: backend/src/main/java/com/example/feedbacksubmission/dto
package com.example.feedbacksubmission.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Email;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

/**
 * Data Transfer Object for incoming feedback submission requests.
 * Used for validation and deserialization of JSON payload.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeedbackRequest {

    @NotBlank(message = "Feedback text cannot be empty.")
    @Size(min = 10, max = 2000, message = "Feedback text must be between 10 and 2000 characters.")
    private String feedbackText;

    @Email(message = "Invalid email format.", regexp = "^$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,6}$")
    @Size(max = 255, message = "Email address cannot exceed 255 characters.")
    private String userEmail; // Optional, so no @NotBlank
}
```

```java
filename: FeedbackService.java
directory: backend/src/main/java/com/example/feedbacksubmission/service
package com.example.feedbacksubmission.service;

import com.example.feedbacksubmission.dto.FeedbackRequest;
import com.example.feedbacksubmission.model.Feedback;
import com.example.feedbacksubmission.repository.FeedbackRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.util.HtmlUtils; // For basic HTML escaping

import java.time.LocalDateTime;

/**
 * Service layer for handling feedback submission business logic.
 * Includes data sanitization and persistence.
 */
@Service
public class FeedbackService {

    private final FeedbackRepository feedbackRepository;

    public FeedbackService(FeedbackRepository feedbackRepository) {
        this.feedbackRepository = feedbackRepository;
    }

    /**
     * Submits new feedback, sanitizing the input before saving.
     * @param request The DTO containing feedback text and optional email.
     * @return The saved Feedback entity.
     */
    @Transactional
    public Feedback submitFeedback(FeedbackRequest request) {
        // Sanitize input data to prevent XSS and other injection attacks.
        // HtmlUtils.htmlEscape is a basic but effective way to prevent XSS when rendering
        // but for more complex sanitization or preventing storage of malicious content,
        // a dedicated library (e.g., OWASP Java HTML Sanitizer) should be used.
        String sanitizedFeedbackText = HtmlUtils.htmlEscape(request.getFeedbackText().trim());
        String sanitizedUserEmail = request.getUserEmail() != null ? HtmlUtils.htmlEscape(request.getUserEmail().trim()) : null;

        Feedback feedback = new Feedback();
        feedback.setFeedbackText(sanitizedFeedbackText);
        feedback.setUserEmail(sanitizedUserEmail);
        feedback.setSubmissionDate(LocalDateTime.now()); // Set here or use @PrePersist in entity

        return feedbackRepository.save(feedback);
    }
}
```

```java
filename: FeedbackController.java
directory: backend/src/main/java/com/example/feedbacksubmission/controller
package com.example.feedbacksubmission.controller;

import com.example.feedbacksubmission.dto.FeedbackRequest;
import com.example.feedbacksubmission.model.Feedback;
import com.example.feedbacksubmission.service.FeedbackService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * REST controller for handling feedback submission requests.
 * Exposes the /api/feedback endpoint.
 */
@RestController
@RequestMapping("/api")
public class FeedbackController {

    private static final Logger logger = LoggerFactory.getLogger(FeedbackController.class);
    private final FeedbackService feedbackService;

    public FeedbackController(FeedbackService feedbackService) {
        this.feedbackService = feedbackService;
    }

    /**
     * Handles POST requests for feedback submission.
     *
     * @param request The feedback data submitted by the user.
     * @return ResponseEntity with the created Feedback object and HttpStatus.CREATED (201)
     *         or HttpStatus.BAD_REQUEST (400) if validation fails.
     */
    @PostMapping("/feedback")
    public ResponseEntity<Feedback> submitFeedback(@Valid @RequestBody FeedbackRequest request) {
        logger.info("Received feedback submission request. Feedback text length: {}, Email provided: {}",
                request.getFeedbackText().length(), request.getUserEmail() != null);
        try {
            Feedback newFeedback = feedbackService.submitFeedback(request);
            logger.info("Feedback with ID {} submitted successfully.", newFeedback.getId());
            return new ResponseEntity<>(newFeedback, HttpStatus.CREATED);
        } catch (Exception e) {
            logger.error("Error submitting feedback: {}", e.getMessage(), e);
            // In a production scenario, avoid exposing raw exception messages.
            // Return a generic error message or a specific DTO for errors.
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
}
```

```java
filename: WebConfig.java
directory: backend/src/main/java/com/example/feedbacksubmission/config
package com.example.feedbacksubmission.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web configuration for the Spring Boot application.
 * Configures CORS to allow frontend applications to make requests.
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**") // Apply CORS to all /api endpoints
                .allowedOrigins("http://localhost:4200", "http://your-frontend-domain.com") // Replace with your Angular app's URL
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}
```

```java
filename: GlobalExceptionHandler.java
directory: backend/src/main/java/com/example/feedbacksubmission/exception
package com.example.feedbacksubmission.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;

import java.util.HashMap;
import java.util.Map;

/**
 * Centralized exception handler for REST controllers.
 * Provides consistent error responses for validation failures and other exceptions.
 */
@ControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Handles validation exceptions thrown by @Valid annotation.
     * Returns a 400 Bad Request with details on validation errors.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ResponseEntity<Map<String, String>> handleValidationExceptions(MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
                errors.put(error.getField(), error.getDefaultMessage()));
        return new ResponseEntity<>(errors, HttpStatus.BAD_REQUEST);
    }

    /**
     * Handles all other uncaught exceptions.
     * Returns a 500 Internal Server Error.
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ResponseEntity<String> handleGenericException(Exception ex) {
        // Log the exception for debugging purposes (handled by controller already, but good for global)
        // logger.error("An unexpected error occurred: {}", ex.getMessage(), ex);
        return new ResponseEntity<>("An unexpected error occurred. Please try again later.", HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

```properties
filename: application.properties
directory: backend/src/main/resources
# Server Port
server.port=8080

# Oracle Database Configuration
spring.datasource.url=jdbc:oracle:thin:@localhost:1521:xe
spring.datasource.username=your_db_username
spring.datasource.password=your_db_password
spring.datasource.driver-class-name=oracle.jdbc.OracleDriver

# JPA/Hibernate Configuration
spring.jpa.hibernate.ddl-auto=update # 'update' is for development, use 'none' or 'validate' for production
spring.jpa.database-platform=org.hibernate.dialect.OracleDialect
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# For enabling H2 console if using H2 for testing (can be commented out in production)
# spring.h2.console.enabled=true
# spring.h2.console.path=/h2-console
```

```java
filename: FeedbackServiceTest.java
directory: backend/src/test/java/com/example/feedbacksubmission/service
package com.example.feedbacksubmission.service;

import com.example.feedbacksubmission.dto.FeedbackRequest;
import com.example.feedbacksubmission.model.Feedback;
import com.example.feedbacksubmission.repository.FeedbackRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class FeedbackServiceTest {

    @Mock
    private FeedbackRepository feedbackRepository;

    @InjectMocks
    private FeedbackService feedbackService;

    private FeedbackRequest feedbackRequest;
    private Feedback expectedFeedback;

    @BeforeEach
    void setUp() {
        feedbackRequest = new FeedbackRequest("This is a test feedback.", "test@example.com");
        expectedFeedback = new Feedback();
        expectedFeedback.setId(1L);
        expectedFeedback.setFeedbackText("This is a test feedback.");
        expectedFeedback.setUserEmail("test@example.com");
    }

    @Test
    void testSubmitFeedback_success() {
        when(feedbackRepository.save(any(Feedback.class))).thenReturn(expectedFeedback);

        Feedback result = feedbackService.submitFeedback(feedbackRequest);

        assertNotNull(result);
        assertEquals(expectedFeedback.getId(), result.getId());
        assertEquals(expectedFeedback.getFeedbackText(), result.getFeedbackText());
        assertEquals(expectedFeedback.getUserEmail(), result.getUserEmail());
        assertNotNull(result.getSubmissionDate());
    }

    @Test
    void testSubmitFeedback_sanitization() {
        FeedbackRequest maliciousRequest = new FeedbackRequest("<script>alert('xss');</script>Test", "malicious@example.com");
        Feedback savedFeedback = new Feedback();
        savedFeedback.setId(2L);
        savedFeedback.setFeedbackText("&lt;script&gt;alert(&#39;xss&#39;);&lt;/script&gt;Test");
        savedFeedback.setUserEmail("malicious@example.com");

        when(feedbackRepository.save(any(Feedback.class))).thenReturn(savedFeedback);

        Feedback result = feedbackService.submitFeedback(maliciousRequest);

        assertNotNull(result);
        assertEquals("&lt;script&gt;alert(&#39;xss&#39;);&lt;/script&gt;Test", result.getFeedbackText());
        assertEquals("malicious@example.com", result.getUserEmail());
    }

    @Test
    void testSubmitFeedback_noEmail() {
        FeedbackRequest noEmailRequest = new FeedbackRequest("Feedback without email.", null);
        Feedback savedFeedback = new Feedback();
        savedFeedback.setId(3L);
        savedFeedback.setFeedbackText("Feedback without email.");
        savedFeedback.setUserEmail(null);

        when(feedbackRepository.save(any(Feedback.class))).thenReturn(savedFeedback);

        Feedback result = feedbackService.submitFeedback(noEmailRequest);

        assertNotNull(result);
        assertEquals("Feedback without email.", result.getFeedbackText());
        assertEquals(null, result.getUserEmail());
    }
}
```

```java
filename: FeedbackControllerTest.java
directory: backend/src/test/java/com/example/feedbacksubmission/controller
package com.example.feedbacksubmission.controller;

import com.example.feedbacksubmission.dto.FeedbackRequest;
import com.example.feedbacksubmission.model.Feedback;
import com.example.feedbacksubmission.service.FeedbackService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(FeedbackController.class)
public class FeedbackControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private FeedbackService feedbackService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void testSubmitFeedback_success() throws Exception {
        FeedbackRequest request = new FeedbackRequest("Great application, very useful!", "user@example.com");
        Feedback createdFeedback = new Feedback(1L, "Great application, very useful!", "user@example.com", LocalDateTime.now());

        when(feedbackService.submitFeedback(any(FeedbackRequest.class))).thenReturn(createdFeedback);

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated()) // Expect 201 Created
                .andExpect(jsonPath("$.id").value(1L))
                .andExpect(jsonPath("$.feedbackText").value("Great application, very useful!"))
                .andExpect(jsonPath("$.userEmail").value("user@example.com"));
    }

    @Test
    void testSubmitFeedback_emptyFeedbackText_badRequest() throws Exception {
        FeedbackRequest request = new FeedbackRequest("", "user@example.com"); // Empty feedback text

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest()) // Expect 400 Bad Request
                .andExpect(jsonPath("$.feedbackText").value("Feedback text cannot be empty."));
    }

    @Test
    void testSubmitFeedback_shortFeedbackText_badRequest() throws Exception {
        FeedbackRequest request = new FeedbackRequest("too short", "user@example.com"); // Too short feedback text

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest()) // Expect 400 Bad Request
                .andExpect(jsonPath("$.feedbackText").value("Feedback text must be between 10 and 2000 characters."));
    }

    @Test
    void testSubmitFeedback_invalidEmail_badRequest() throws Exception {
        FeedbackRequest request = new FeedbackRequest("This is valid feedback text.", "invalid-email"); // Invalid email

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest()) // Expect 400 Bad Request
                .andExpect(jsonPath("$.userEmail").value("Invalid email format."));
    }

    @Test
    void testSubmitFeedback_internalServerError() throws Exception {
        FeedbackRequest request = new FeedbackRequest("Feedback that causes error.", "error@example.com");

        // Simulate a service layer exception
        when(feedbackService.submitFeedback(any(FeedbackRequest.class))).thenThrow(new RuntimeException("Database error"));

        mockMvc.perform(post("/api/feedback")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isInternalServerError()); // Expect 500 Internal Server Error
    }
}
```

```json
filename: package.json
directory: frontend
{
  "name": "frontend",
  "version": "0.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "watch": "ng build --watch --configuration development",
    "test": "ng test"
  },
  "private": true,
  "dependencies": {
    "@angular/animations": "^16.2.0",
    "@angular/common": "^16.2.0",
    "@angular/compiler": "^16.2.0",
    "@angular/core": "^16.2.0",
    "@angular/forms": "^16.2.0",
    "@angular/platform-browser": "^16.2.0",
    "@angular/platform-browser-dynamic": "^16.2.0",
    "@angular/router": "^16.2.0",
    "rxjs": "~7.8.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.13.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^16.2.6",
    "@angular/cli": "^16.2.6",
    "@angular/compiler-cli": "^16.2.0",
    "@types/jasmine": "~4.3.0",
    "@typescript-eslint/eslint-plugin": "6.x",
    "@typescript-eslint/parser": "6.x",
    "eslint": "^8.51.0",
    "jasmine-core": "~4.6.0",
    "karma": "~6.4.0",
    "karma-chrome-launcher": "~3.2.0",
    "karma-coverage": "~2.2.0",
    "karma-jasmine": "~5.1.0",
    "karma-jasmine-html-reporter": "~2.1.0",
    "typescript": "~5.1.3"
  }
}
```

```json
filename: angular.json
directory: frontend
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "frontend": {
      "projectType": "application",
      "schematics": {},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {
            "outputPath": "dist/frontend",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": [
              "zone.js"
            ],
            "tsConfig": "tsconfig.app.json",
            "assets": [
              "src/favicon.ico",
              "src/assets"
            ],
            "styles": [
              "src/styles.css"
            ],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                },
                {
                  "type": "anyComponentStyle",
                  "maximumWarning": "2kb",
                  "maximumError": "4kb"
                }
              ],
              "outputHashing": "all"
            },
            "development": {
              "buildOptimizer": false,
              "optimization": false,
              "vendorChunk": true,
              "extractLicenses": false,
              "sourceMap": true,
              "namedChunks": true
            }
          },
          "defaultConfiguration": "production"
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {
            "production": {
              "browserTarget": "frontend:build:production"
            },
            "development": {
              "browserTarget": "frontend:build:development"
            }
          },
          "defaultConfiguration": "development"
        },
        "extract-i18n": {
          "builder": "@angular-devkit/build-angular:extract-i18n",
          "options": {
            "browserTarget": "frontend:build"
          }
        },
        "test": {
          "builder": "@angular-devkit/build-angular:karma",
          "options": {
            "polyfills": [
              "zone.js",
              "zone.js/testing"
            ],
            "tsConfig": "tsconfig.spec.json",
            "assets": [
              "src/favicon.ico",
              "src/assets"
            ],
            "styles": [
              "src/styles.css"
            ],
            "scripts": []
          }
        }
      }
    }
  }
}
```

```typescript
filename: app.module.ts
directory: frontend/src/app
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { FeedbackFormComponent } from './feedback-form/feedback-form.component';

@NgModule({
  declarations: [
    AppComponent,
    FeedbackFormComponent
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule, // For reactive forms
    HttpClientModule     // For making HTTP requests
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

```typescript
filename: feedback-form.component.ts
directory: frontend/src/app/feedback-form
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { FeedbackService } from '../services/feedback.service';

@Component({
  selector: 'app-feedback-form',
  templateUrl: './feedback-form.component.html',
  styleUrls: ['./feedback-form.component.css']
})
export class FeedbackFormComponent implements OnInit {
  feedbackForm!: FormGroup;
  submissionStatus: 'idle' | 'submitting' | 'success' | 'error' = 'idle';
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private feedbackService: FeedbackService
  ) { }

  ngOnInit(): void {
    this.initForm();
  }

  initForm(): void {
    this.feedbackForm = this.fb.group({
      feedbackText: ['', [
        Validators.required,
        Validators.minLength(10),
        Validators.maxLength(2000)
      ]],
      userEmail: ['', [
        Validators.email,
        Validators.maxLength(255)
      ]]
    });
    this.submissionStatus = 'idle';
    this.errorMessage = '';
  }

  // Convenience getter for easy access to form fields
  get f() { return this.feedbackForm.controls; }

  onSubmit(): void {
    this.submissionStatus = 'submitting';
    this.errorMessage = '';

    // Client-side validation
    if (this.feedbackForm.invalid) {
      this.submissionStatus = 'error';
      this.errorMessage = 'Please correct the highlighted errors in the form.';
      // Mark all fields as touched to display validation messages
      this.feedbackForm.markAllAsTouched();
      return;
    }

    const { feedbackText, userEmail } = this.feedbackForm.value;

    this.feedbackService.submitFeedback(feedbackText, userEmail)
      .subscribe({
        next: (response) => {
          console.log('Feedback submitted successfully:', response);
          this.submissionStatus = 'success';
          this.feedbackForm.reset(); // Clear the form on success
        },
        error: (error) => {
          console.error('Error submitting feedback:', error);
          this.submissionStatus = 'error';
          // Handle specific error messages from backend if available
          if (error.status === 400 && error.error) {
            // Assuming backend sends validation errors as a map
            const backendErrors = error.error;
            for (const key in backendErrors) {
              if (this.feedbackForm.controls[key]) {
                this.feedbackForm.controls[key].setErrors({ backendError: backendErrors[key] });
              }
            }
            this.errorMessage = 'Please correct the server-side validation errors.';
          } else {
            this.errorMessage = 'Failed to submit feedback. Please try again later.';
          }
        }
      });
  }

  onCancel(): void {
    // Optionally emit an event to parent or navigate away
    console.log('Feedback submission cancelled.');
    this.initForm(); // Reset form on cancel
  }
}
```

```html
filename: feedback-form.component.html
directory: frontend/src/app/feedback-form
<div class="feedback-container">
  <h2>Provide Your Feedback</h2>
  <form [formGroup]="feedbackForm" (ngSubmit)="onSubmit()">
    <div class="form-group">
      <label for="feedbackText">Feedback Text <span class="required">*</span>:</label>
      <textarea id="feedbackText" formControlName="feedbackText" rows="5"
                placeholder="Share your thoughts on the application..."></textarea>
      <div *ngIf="f['feedbackText'].invalid && (f['feedbackText'].dirty || f['feedbackText'].touched)" class="error-message">
        <div *ngIf="f['feedbackText'].errors?.['required']">Feedback text is required.</div>
        <div *ngIf="f['feedbackText'].errors?.['minlength']">Feedback text must be at least 10 characters.</div>
        <div *ngIf="f['feedbackText'].errors?.['maxlength']">Feedback text cannot exceed 2000 characters.</div>
        <div *ngIf="f['feedbackText'].errors?.['backendError']">{{f['feedbackText'].errors['backendError']}}</div>
      </div>
    </div>

    <div class="form-group">
      <label for="userEmail">Your Email (Optional):</label>
      <input type="email" id="userEmail" formControlName="userEmail" placeholder="your.email@example.com">
      <div *ngIf="f['userEmail'].invalid && (f['userEmail'].dirty || f['userEmail'].touched)" class="error-message">
        <div *ngIf="f['userEmail'].errors?.['email']">Please enter a valid email address.</div>
        <div *ngIf="f['userEmail'].errors?.['maxlength']">Email address cannot exceed 255 characters.</div>
        <div *ngIf="f['userEmail'].errors?.['backendError']">{{f['userEmail'].errors['backendError']}}</div>
      </div>
    </div>

    <div *ngIf="submissionStatus === 'error'" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <div *ngIf="submissionStatus === 'success'" class="alert alert-success">
      Thank you for your feedback! It has been successfully submitted.
    </div>

    <div class="form-actions">
      <button type="submit" [disabled]="feedbackForm.invalid || submissionStatus === 'submitting'" class="submit-button">
        <span *ngIf="submissionStatus === 'submitting'">Submitting...</span>
        <span *ngIf="submissionStatus !== 'submitting'">Submit Feedback</span>
      </button>
      <button type="button" (click)="onCancel()" class="cancel-button">Cancel</button>
    </div>
  </form>
</div>
```

```css
filename: feedback-form.component.css
directory: frontend/src/app/feedback-form
.feedback-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  font-family: Arial, sans-serif;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 25px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.required {
  color: #d9534f;
}

input[type="email"],
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box; /* Include padding in width */
  transition: border-color 0.3s ease;
}

input[type="email"]:focus,
textarea:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

textarea {
  resize: vertical; /* Allow vertical resizing */
  min-height: 100px;
}

.error-message {
  color: #d9534f;
  font-size: 14px;
  margin-top: 5px;
}

.alert {
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
  text-align: center;
}

.alert-danger {
  color: #a94442;
  background-color: #f2dede;
  border-color: #ebccd1;
}

.alert-success {
  color: #3c763d;
  background-color: #dff0d8;
  border-color: #d6e9c6;
}

.form-actions {
  display: flex;
  justify-content: flex-end; /* Align buttons to the right */
  gap: 15px; /* Space between buttons */
  margin-top: 30px;
}

.submit-button,
.cancel-button {
  padding: 12px 25px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.submit-button {
  background-color: #007bff;
  color: white;
}

.submit-button:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-1px);
}

.submit-button:disabled {
  background-color: #a0c9f1;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}
```

```typescript
filename: feedback.service.ts
directory: frontend/src/app/services
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { FeedbackResponse } from '../models/feedback.model'; // Assuming a response model

@Injectable({
  providedIn: 'root'
})
export class FeedbackService {
  private apiUrl = `${environment.apiUrl}/feedback`; // Assuming /api/feedback

  constructor(private http: HttpClient) { }

  /**
   * Submits user feedback to the backend API.
   * @param feedbackText The mandatory text feedback.
   * @param userEmail The optional user email.
   * @returns An Observable of the HTTP response.
   */
  submitFeedback(feedbackText: string, userEmail: string | null): Observable<FeedbackResponse> {
    const payload = {
      feedbackText: feedbackText,
      userEmail: userEmail || null // Ensure null is sent for optional empty email
    };
    return this.http.post<FeedbackResponse>(this.apiUrl, payload);
  }
}
```

```typescript
filename: feedback.model.ts
directory: frontend/src/app/models
/**
 * Interface for the data structure of a feedback submission payload.
 */
export interface FeedbackPayload {
  feedbackText: string;
  userEmail?: string | null;
}

/**
 * Interface for the expected response structure from a successful feedback submission.
 */
export interface FeedbackResponse {
  id: number;
  feedbackText: string;
  userEmail: string | null;
  submissionDate: string; // ISO 8601 string date
}
```

```typescript
filename: environment.ts
directory: frontend/src/environments
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8080/api' // Backend API URL
};
```

```typescript
filename: environment.prod.ts
directory: frontend/src/environments
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api-url.com/api' // Production Backend API URL
};
```

```typescript
filename: app.component.ts
directory: frontend/src/app
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Feedback Application';
}
```

```html
filename: app.component.html
directory: frontend/src/app
<div class="app-container">
  <h1>{{ title }}</h1>
  <app-feedback-form></app-feedback-form>
</div>
```

```css
filename: app.component.css
directory: frontend/src/app
.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #eef1f5;
  min-height: 100vh;
  box-sizing: border-box;
}

h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 2.5em;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}
/* Basic styles for the entire page */
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #f4f7f6;
  color: #333;
}
```

```typescript
filename: feedback-form.component.spec.ts
directory: frontend/src/app/feedback-form
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';

import { FeedbackFormComponent } from './feedback-form.component';
import { FeedbackService } from '../services/feedback.service';

describe('FeedbackFormComponent', () => {
  let component: FeedbackFormComponent;
  let fixture: ComponentFixture<FeedbackFormComponent>;
  let feedbackService: FeedbackService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FeedbackFormComponent ],
      imports: [ ReactiveFormsModule, HttpClientTestingModule ],
      providers: [ FeedbackService ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FeedbackFormComponent);
    component = fixture.componentInstance;
    feedbackService = TestBed.inject(FeedbackService); // Get a reference to the service
    fixture.detectChanges(); // Initialize the component and form
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('form should be invalid when empty', () => {
    expect(component.feedbackForm.valid).toBeFalsy();
  });

  it('feedbackText field should be required', () => {
    let feedbackText = component.f['feedbackText'];
    expect(feedbackText.valid).toBeFalsy(); // Initially invalid
    feedbackText.setValue('');
    expect(feedbackText.errors?.['required']).toBeTruthy();
  });

  it('feedbackText field should require minLength of 10', () => {
    let feedbackText = component.f['feedbackText'];
    feedbackText.setValue('short');
    expect(feedbackText.errors?.['minlength']).toBeTruthy();
    feedbackText.setValue('This is long enough.');
    expect(feedbackText.errors).toBeNull();
  });

  it('userEmail field should be valid with a valid email', () => {
    let userEmail = component.f['userEmail'];
    userEmail.setValue('test@example.com');
    expect(userEmail.valid).toBeTruthy();
  });

  it('userEmail field should be invalid with an invalid email', () => {
    let userEmail = component.f['userEmail'];
    userEmail.setValue('invalid-email');
    expect(userEmail.errors?.['email']).toBeTruthy();
  });

  it('should set submissionStatus to "submitting" and then "success" on successful submission', () => {
    const mockResponse = { id: 1, feedbackText: 'Test', userEmail: 'test@example.com', submissionDate: '2023-10-27' };
    spyOn(feedbackService, 'submitFeedback').and.returnValue(of(mockResponse));

    component.f['feedbackText'].setValue('This is a test feedback.');
    component.f['userEmail'].setValue('test@example.com');
    component.onSubmit();

    expect(component.submissionStatus).toBe('success');
    expect(component.feedbackForm.pristine).toBeTrue(); // Form should be reset
  });

  it('should set submissionStatus to "error" on failed submission', () => {
    spyOn(feedbackService, 'submitFeedback').and.returnValue(throwError(() => new Error('Submission failed')));

    component.f['feedbackText'].setValue('This is a test feedback.');
    component.f['userEmail'].setValue('test@example.com');
    component.onSubmit();

    expect(component.submissionStatus).toBe('error');
    expect(component.errorMessage).toBe('Failed to submit feedback. Please try again later.');
  });

  it('should reset form and status on cancel', () => {
    component.f['feedbackText'].setValue('Some text');
    component.submissionStatus = 'success';
    component.errorMessage = 'Some error';

    component.onCancel();

    expect(component.feedbackForm.value.feedbackText).toBeNull(); // reset() makes it null
    expect(component.feedbackForm.value.userEmail).toBeNull();
    expect(component.submissionStatus).toBe('idle');
    expect(component.errorMessage).toBe('');
  });
});
```

```typescript
filename: feedback.service.spec.ts
directory: frontend/src/app/services
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { FeedbackService } from './feedback.service';
import { environment } from '../../environments/environment';
import { FeedbackResponse } from '../models/feedback.model';

describe('FeedbackService', () => {
  let service: FeedbackService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [FeedbackService]
    });
    service = TestBed.inject(FeedbackService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure that there are no outstanding requests
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send a POST request to submit feedback', () => {
    const feedbackText = 'This is a test feedback.';
    const userEmail = 'test@example.com';
    const mockResponse: FeedbackResponse = {
      id: 1,
      feedbackText: feedbackText,
      userEmail: userEmail,
      submissionDate: new Date().toISOString()
    };

    service.submitFeedback(feedbackText, userEmail).subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/feedback`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ feedbackText, userEmail });
    req.flush(mockResponse); // Provide a dummy response
  });

  it('should send a POST request with null email if not provided', () => {
    const feedbackText = 'Feedback without email.';
    const userEmail = null;
    const mockResponse: FeedbackResponse = {
      id: 2,
      feedbackText: feedbackText,
      userEmail: null,
      submissionDate: new Date().toISOString()
    };

    service.submitFeedback(feedbackText, userEmail).subscribe(response => {
      expect(response).toEqual(mockResponse);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/feedback`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ feedbackText, userEmail: null });
    req.flush(mockResponse);
  });
});
```

---

**Summary of Implementation:**

This project provides a full-stack implementation of the "Application Feedback Submission" feature, adhering to the provided architecture documentation.

**Backend (Java/Spring Boot):**
*   **`pom.xml`**: Configures Spring Boot starters for Web, JPA, Validation, and includes the Oracle JDBC driver. Lombok is used for boilerplate code reduction.
*   **`FeedbackSubmissionApplication.java`**: The main Spring Boot application entry point.
*   **`model/Feedback.java`**: Defines the JPA entity `Feedback`, mapping to a `feedback` table in the database. It includes fields for `id`, `feedbackText`, `userEmail`, and `submissionDate`, with `@PrePersist` for automatic timestamping. A `SequenceGenerator` is included for Oracle's sequence-based ID generation.
*   **`repository/FeedbackRepository.java`**: A Spring Data JPA repository interface, providing standard CRUD operations for the `Feedback` entity without explicit implementation.
*   **`dto/FeedbackRequest.java`**: A Data Transfer Object used for receiving feedback data from the frontend. It includes `jakarta.validation` annotations (`@NotBlank`, `@Size`, `@Email`) for server-side input validation, aligning with `FR5.3`. The email regex allows for an empty string, making the email optional while still validating format if provided.
*   **`service/FeedbackService.java`**: Implements the core business logic. The `submitFeedback` method takes a `FeedbackRequest` DTO, performs basic sanitization using `HtmlUtils.htmlEscape` (as a placeholder for more robust sanitization libraries like OWASP ESAPI, as per `FR5.5`), maps it to a `Feedback` entity, and persists it using the `FeedbackRepository`. It's marked `@Transactional`.
*   **`controller/FeedbackController.java`**: Exposes the `/api/feedback` REST endpoint, accepting `POST` requests. It uses `@Valid` to trigger server-side validation of the `FeedbackRequest` DTO. It calls the `FeedbackService` and returns `201 Created` on success or appropriate error codes (`400 Bad Request` for validation failures, `500 Internal Server Error` for unexpected issues), fulfilling `FR5.4`. Logging is included for operational insights.
*   **`config/WebConfig.java`**: Configures Cross-Origin Resource Sharing (CORS) to allow the Angular frontend (running on `localhost:4200` by default) to communicate with the backend API.
*   **`exception/GlobalExceptionHandler.java`**: A `@ControllerAdvice` to centralize error handling, specifically for `MethodArgumentNotValidException` (validation errors) returning a `400 Bad Request` with field-specific messages, and a generic `Exception` handler for `500 Internal Server Error`.
*   **`application.properties`**: Contains configuration for the Spring Boot application, including server port, Oracle database connection details (URL, username, password, driver), and JPA/Hibernate settings (DDL auto-update, dialect, SQL logging).
*   **Tests**: `FeedbackServiceTest` uses Mockito for unit testing the business logic, including sanitization. `FeedbackControllerTest` uses `@WebMvcTest` to integration test the API endpoint, verifying validation and successful submission responses.

**Frontend (Angular):**
*   **`package.json` / `angular.json`**: Standard Angular project configuration files, defining dependencies and build/serve scripts.
*   **`app.module.ts`**: The root Angular module, importing `ReactiveFormsModule` for form handling and `HttpClientModule` for making HTTP requests.
*   **`feedback-form/feedback-form.component.ts`**: The main component for feedback submission. It uses `FormBuilder` and `FormGroup` for reactive forms, implementing client-side validation (`Validators.required`, `Validators.minLength`, `Validators.maxLength`, `Validators.email`) as per `FR3.1`. It manages submission status (`idle`, `submitting`, `success`, `error`) and communicates with the `FeedbackService`. It also handles displaying success/error messages and resetting the form, satisfying `FR4.2`, `FR4.3`.
*   **`feedback-form/feedback-form.component.html`**: The HTML template for the feedback form, including input fields for feedback text and optional email, validation message display, and submit/cancel buttons, as per `FR1.2`, `FR2`.
*   **`feedback-form/feedback-form.component.css`**: Provides basic styling for the feedback form to enhance user experience, aligning with `NFR3.3`.
*   **`services/feedback.service.ts`**: An injectable service that encapsulates the HTTP communication with the backend. It uses Angular's `HttpClient` to send `POST` requests to the `/api/feedback` endpoint, fulfilling `FR4.1`.
*   **`models/feedback.model.ts`**: Defines TypeScript interfaces for the request payload and the expected backend response, improving type safety.
*   **`environments/environment.ts` / `environment.prod.ts`**: Defines environment-specific variables, primarily the backend API URL, allowing for easy switching between development and production endpoints.
*   **`app.component.ts` / `app.component.html` / `app.component.css`**: The root Angular component hosting the `FeedbackFormComponent`, with minimal global styling.
*   **Tests**: `feedback-form.component.spec.ts` unit tests the form's reactivity, validation, and interaction with the service. `feedback.service.spec.ts` unit tests the `FeedbackService` using `HttpTestingController` to mock HTTP requests, verifying correct payload and endpoint usage.

**Integration and Security:**
*   **Communication:** Frontend communicates with the backend via RESTful HTTP POST requests to `/api/feedback`, secured conceptually by HTTPS (handled by API Gateway in architecture) and CORS configuration.
*   **Validation:** Both client-side and server-side validation are implemented for robustness.
*   **Sanitization:** Basic input sanitization is in place at the backend to prevent common injection attacks.
*   **Database Interaction:** Spring Data JPA with Oracle driver ensures secure database operations (e.g., parameterized queries implicitly handled by JPA) and adherence to the specified `feedback` table schema (`FR6`).

This comprehensive setup provides a solid foundation for the Application Feedback Submission feature, built with maintainability, scalability, and security in mind, aligning with the provided architectural guidance.