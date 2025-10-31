# 🧪 Testing & QA Checklist - Secure E2EE Chat

## Table of Contents
- [Manual Testing Guide](#manual-testing-guide)
- [API Testing](#api-testing)
- [Security Testing](#security-testing)
- [Performance Testing](#performance-testing)
- [Browser Compatibility](#browser-compatibility)
- [QA Checklist](#qa-checklist)

---

## Manual Testing Guide

### Test Environment Setup

1. **Local Development**:
   - Backend: http://localhost:8001
   - Frontend: http://localhost:3000
   - Use 2+ browsers/incognito windows for multi-user testing

2. **Production/Staging**:
   - Use deployed URLs
   - Test from different networks/locations
   - Test on mobile devices

---

### Test Case 1: User Registration

**Objective**: Verify new user can register successfully

**Steps**:
1. Open http://localhost:3000
2. Click **"Register"** tab
3. Enter username: `testuser1` (min 3 chars)
4. Enter password: `password123` (min 8 chars)
5. Click **"Create Account"**

**Expected Results**:
- ✅ Loading spinner appears
- ✅ Registration completes in <2 seconds
- ✅ Automatically redirected to chat interface
- ✅ Username displayed in sidebar
- ✅ Status shows "Connected"

**Verify in Browser DevTools**:
- IndexedDB → SecureChatDB → crypto_keys → Contains `privateKey_[user_id]`
- LocalStorage → Contains: `access_token`, `user_id`, `username`

**Error Cases to Test**:
- Username too short (< 3 chars): Should show error
- Password too short (< 8 chars): Should show error
- Duplicate username: Should show "Username already registered"
- Special characters in username: Should show validation error

---

### Test Case 2: User Login

**Objective**: Verify existing user can login

**Steps**:
1. After registering, click logout button
2. Click **"Login"** tab
3. Enter registered username and password
4. Click **"Login"**

**Expected Results**:
- ✅ Login successful, redirected to chat
- ✅ Private key retrieved from IndexedDB
- ✅ WebSocket connection established
- ✅ User list loads

**Error Cases to Test**:
- Wrong password: Should show "Invalid username or password"
- Non-existent username: Should show "Invalid username or password"
- Missing private key in IndexedDB: Should show "Private key not found"

---

### Test Case 3: Send Encrypted Message

**Objective**: Verify E2EE message flow

**Preparation**:
- Register 2 users in different browsers:
  - Browser 1: `alice`
  - Browser 2: `bob`

**Steps (as Alice)**:
1. Login as `alice`
2. Click on `bob` in users list
3. Type message: "Hello Bob! This is encrypted 🔒"
4. Click send button (paper plane icon)

**Expected Results (Alice's view)**:
- ✅ Message appears immediately in chat (optimistic update)
- ✅ Message shown with blue background (own message)
- ✅ Timestamp displayed
- ✅ Send button disabled while sending
- ✅ Input field cleared after send

**Expected Results (Bob's view)**:
- ✅ Message appears in chat within 1 second
- ✅ Message shown with white background (received message)
- ✅ Message decrypted and displayed correctly
- ✅ Timestamp matches

**Verify Encryption in Network Tab**:
1. Open DevTools → Network → WS (WebSocket)
2. Click on WebSocket connection
3. Check Messages tab
4. Find sent message
5. Verify payload contains `ciphertext` (base64 encoded)
6. **CRITICAL**: Plaintext "Hello Bob" should NOT appear in ciphertext

**Example WebSocket payload**:
```json
{
  "to_user_id": "abc-123",
  "ciphertext": "K8vQ2x9... [long base64 string]"
}
```

---

### Test Case 4: Receive Encrypted Message

**Objective**: Verify message reception and decryption

**Steps (as Bob)**:
1. Ensure Bob is logged in and viewing chat
2. Alice sends message "Test message from Alice"
3. Observe Bob's chat interface

**Expected Results**:
- ✅ Message appears automatically (no refresh needed)
- ✅ Message decrypted successfully
- ✅ Plaintext displayed: "Test message from Alice"
- ✅ Sender identified correctly
- ✅ Auto-scroll to newest message

**Error Cases**:
- If decryption fails: Should show error message
- If private key missing: Should prompt re-login
- If WebSocket disconnected: Should show "Disconnected" status

---

### Test Case 5: Multi-User Chat

**Objective**: Verify multiple simultaneous chats

**Preparation**:
- 3 users: Alice, Bob, Charlie

**Steps**:
1. Alice sends message to Bob
2. Bob sends message to Charlie
3. Charlie sends message to Alice
4. Verify each user only sees their intended messages

**Expected Results**:
- ✅ Alice sees: messages to/from Bob, messages to/from Charlie
- ✅ Bob sees: messages to/from Alice, messages to/from Charlie
- ✅ Charlie sees: messages to/from Bob, messages to/from Alice
- ✅ No message leakage between conversations
- ✅ Message counts update correctly in user list

---

### Test Case 6: WebSocket Reconnection

**Objective**: Verify auto-reconnect on network issues

**Steps**:
1. Login as user
2. Open DevTools → Network → Throttling
3. Select "Offline"
4. Wait 5 seconds
5. Observe status indicator (should show "Disconnected")
6. Select "Online"
7. Wait 3 seconds

**Expected Results**:
- ✅ Status changes to "Disconnected" when offline
- ✅ Status changes back to "Connected" within 3 seconds of going online
- ✅ No data loss
- ✅ Can send messages after reconnection

---

### Test Case 7: Logout

**Objective**: Verify secure logout

**Steps**:
1. Login as user
2. Click logout button
3. Verify redirected to login page

**Expected Results**:
- ✅ Redirected to auth screen
- ✅ WebSocket connection closed
- ✅ LocalStorage cleared: `access_token`, `user_id`, `username`
- ✅ **CRITICAL**: Private key deleted from IndexedDB

**Verify**:
- IndexedDB → SecureChatDB → crypto_keys → Should be empty
- Attempting to navigate to chat URL should redirect to login

---

## API Testing

### Using cURL

#### 1. Health Check
```bash
curl http://localhost:8001/health
```
**Expected**: `{"status":"healthy"}`

#### 2. Register User
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "apitest",
    "password": "password123",
    "public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
  }'
```
**Expected**: 
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "username": "apitest"
}
```

#### 3. Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "apitest",
    "password": "password123"
  }'
```

#### 4. Get Users (requires JWT)
```bash
TOKEN="your_jwt_token_here"
curl http://localhost:8001/api/v1/users \
  -H "Authorization: Bearer $TOKEN"
```
**Expected**: Array of users

#### 5. Get Public Key
```bash
TOKEN="your_jwt_token_here"
USER_ID="target_user_id"
curl http://localhost:8001/api/v1/keys/$USER_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### 6. WebSocket Test (using wscat)
```bash
# Install wscat
npm install -g wscat

# Connect (replace TOKEN)
wscat -c "ws://localhost:8001/ws/YOUR_JWT_TOKEN"

# After connected, send message:
{"to_user_id":"recipient_id","ciphertext":"encrypted_content"}
```

---

## Security Testing

### 1. Zero-Knowledge Verification

**Test**: Verify server never sees plaintext

**Steps**:
1. Send encrypted message via WebSocket
2. Check backend logs: `tail -f /var/log/supervisor/backend.out.log`
3. Check database: Query messages table

**Expected**:
- ✅ Logs show only ciphertext (base64)
- ✅ Database `messages.ciphertext` column contains only encrypted data
- ✅ No plaintext visible anywhere in server logs/database

**Database Query**:
```sql
SELECT ciphertext FROM messages LIMIT 1;
-- Should show long base64 string, not readable text
```

---

### 2. Private Key Security

**Test**: Verify private key never transmitted

**Steps**:
1. Register new user
2. Open DevTools → Network → All
3. Filter by "key" or search for base64 strings
4. Check all request/response payloads

**Expected**:
- ✅ Only PUBLIC key sent to server during registration
- ✅ Private key NEVER appears in network requests
- ✅ Private key only in IndexedDB (client-side storage)

---

### 3. JWT Token Security

**Test**: Verify token expiration and validation

**Steps**:
1. Login and capture JWT token
2. Decode token at [jwt.io](https://jwt.io)
3. Verify claims: `sub` (user_id), `exp` (expiration)
4. Wait for token to expire (or manually edit)
5. Try to access `/api/v1/users` with expired token

**Expected**:
- ✅ Valid token works
- ✅ Expired token returns 401 Unauthorized
- ✅ Invalid token returns 401 Unauthorized
- ✅ Missing token returns 401 Unauthorized

---

### 4. SQL Injection Test

**Test**: Attempt SQL injection via inputs

**Attempts**:
```bash
# Username with SQL
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'"'"' OR '"'"'1'"'"'='"'"'1","password":"test","public_key":"test"}'

# Password with SQL
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"'"'"' OR '"'"'1'"'"'='"'"'1"}'
```

**Expected**:
- ✅ All attempts fail gracefully
- ✅ No SQL execution
- ✅ SQLAlchemy ORM prevents injection
- ✅ Proper error messages

---

### 5. XSS (Cross-Site Scripting) Test

**Test**: Attempt to inject JavaScript

**Steps**:
1. Register with username: `<script>alert('XSS')</script>`
2. Send message: `<img src=x onerror=alert('XSS')>`

**Expected**:
- ✅ Scripts not executed
- ✅ Content rendered as plain text
- ✅ React automatically escapes HTML

---

### 6. CORS Test

**Test**: Verify CORS protection

**Steps**:
1. Open browser console on different domain (e.g., google.com)
2. Try to call API:
```javascript
fetch('http://localhost:8001/api/v1/users')
  .then(r => r.json())
  .then(console.log)
```

**Expected**:
- ✅ CORS error (if origins restricted)
- ✅ Or successful if `allow_origins=["*"]` (development mode)

---

## Performance Testing

### 1. Encryption Speed Test

**Test in Browser Console**:
```javascript
// Generate key pair
const keyPair = await window.crypto.subtle.generateKey(
  {
    name: "RSA-OAEP",
    modulusLength: 2048,
    publicExponent: new Uint8Array([1, 0, 1]),
    hash: "SHA-256",
  },
  true,
  ["encrypt", "decrypt"]
);

// Encrypt message
const message = "Test message";
const encoder = new TextEncoder();
const data = encoder.encode(message);

const startEncrypt = performance.now();
const encrypted = await window.crypto.subtle.encrypt(
  { name: "RSA-OAEP" },
  keyPair.publicKey,
  data
);
const encryptTime = performance.now() - startEncrypt;

console.log(`Encryption took: ${encryptTime.toFixed(2)}ms`);

// Decrypt message
const startDecrypt = performance.now();
const decrypted = await window.crypto.subtle.decrypt(
  { name: "RSA-OAEP" },
  keyPair.privateKey,
  encrypted
);
const decryptTime = performance.now() - startDecrypt;

console.log(`Decryption took: ${decryptTime.toFixed(2)}ms`);
```

**Expected**:
- ✅ Encryption: <20ms
- ✅ Decryption: <30ms

---

### 2. Load Testing

**Using k6**:
```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 50 },  // Ramp up to 50 users
    { duration: '1m', target: 50 },   // Stay at 50 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    errors: ['rate<0.1'],              // Error rate < 10%
    http_req_duration: ['p(95)<500'],  // 95% < 500ms
  },
};

export default function () {
  // Test health endpoint
  let res = http.get('http://localhost:8001/health');
  
  let checkRes = check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(!checkRes);
  sleep(1);
}
```

**Run**:
```bash
k6 run load-test.js
```

**Expected**:
- ✅ Error rate < 10%
- ✅ 95th percentile < 500ms
- ✅ No memory leaks

---

## Browser Compatibility

### Desktop Browsers

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | 90+ | ✅ Supported | Web Crypto API fully supported |
| Firefox | 88+ | ✅ Supported | Web Crypto API fully supported |
| Safari | 14+ | ✅ Supported | Web Crypto API fully supported |
| Edge | 90+ | ✅ Supported | Chromium-based, same as Chrome |
| Opera | 76+ | ✅ Supported | Chromium-based |

### Mobile Browsers

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome Mobile | 90+ | ✅ Supported | |
| Safari iOS | 14+ | ✅ Supported | |
| Firefox Mobile | 88+ | ✅ Supported | |
| Samsung Internet | 14+ | ✅ Supported | |

### Known Limitations

- **IE 11**: ❌ Not supported (no Web Crypto API)
- **Safari < 14**: ⚠️ Limited support (older Crypto API)
- **Private/Incognito**: ✅ Supported (IndexedDB available)

---

## QA Checklist

### ✅ Functionality

- [ ] User registration works
- [ ] User login works
- [ ] User logout works and clears data
- [ ] Users list loads correctly
- [ ] User selection works
- [ ] Send message works
- [ ] Receive message works
- [ ] Messages decrypt correctly
- [ ] WebSocket connects automatically
- [ ] WebSocket reconnects on disconnect
- [ ] Multiple simultaneous chats work
- [ ] Message timestamps are accurate
- [ ] Optimistic UI updates work

### ✅ Security

- [ ] Private keys stored only in IndexedDB
- [ ] Private keys never transmitted over network
- [ ] Public keys stored on server
- [ ] Messages encrypted before sending
- [ ] Server never sees plaintext
- [ ] Database stores only ciphertext
- [ ] JWT tokens validated correctly
- [ ] Expired tokens rejected
- [ ] Passwords hashed with bcrypt
- [ ] SQL injection prevented
- [ ] XSS attacks prevented
- [ ] CORS configured correctly

### ✅ UI/UX

- [ ] Responsive design works on mobile
- [ ] Loading states shown appropriately
- [ ] Error messages clear and helpful
- [ ] Success feedback provided
- [ ] Auto-scroll to latest message
- [ ] Connection status indicator works
- [ ] User avatars display correctly
- [ ] Message bubbles styled correctly
- [ ] Timestamp formatting correct
- [ ] Smooth animations
- [ ] No UI jank or freezing

### ✅ Performance

- [ ] Page load < 3 seconds
- [ ] Message send < 1 second
- [ ] Message receive < 1 second
- [ ] Encryption < 50ms per message
- [ ] Decryption < 50ms per message
- [ ] No memory leaks
- [ ] Efficient re-renders
- [ ] WebSocket latency acceptable

### ✅ Error Handling

- [ ] Network errors handled gracefully
- [ ] Invalid credentials show error
- [ ] Duplicate username shows error
- [ ] Validation errors clear
- [ ] Decryption failures handled
- [ ] WebSocket errors handled
- [ ] Database errors handled
- [ ] Empty states shown appropriately

### ✅ Accessibility

- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Color contrast sufficient
- [ ] Screen reader compatible
- [ ] Form labels associated correctly

### ✅ Cross-Browser

- [ ] Chrome works
- [ ] Firefox works
- [ ] Safari works
- [ ] Edge works
- [ ] Mobile Chrome works
- [ ] Mobile Safari works

### ✅ Data Persistence

- [ ] Auth persists across page refresh
- [ ] Private key persists in IndexedDB
- [ ] Message history persists (backend)
- [ ] Logout clears all data

---

## Bug Reporting Template

When reporting bugs, include:

```
**Environment:**
- OS: [e.g., macOS 13.0]
- Browser: [e.g., Chrome 120]
- Backend URL: [e.g., http://localhost:8001]
- Frontend URL: [e.g., http://localhost:3000]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Result:**


**Actual Result:**


**Screenshots/Logs:**


**Additional Context:**

```

---

## Testing Schedule

### Before Each Deployment

1. Run all manual test cases
2. Execute API tests
3. Run load tests
4. Check security tests
5. Verify browser compatibility
6. Review QA checklist

### Weekly

- Security audit
- Performance benchmarks
- Dependency updates
- Database backup verification

### Monthly

- Penetration testing
- Comprehensive load testing
- User acceptance testing
- Security updates

---

**Testing is critical for E2EE applications. Never skip security tests in production!**
