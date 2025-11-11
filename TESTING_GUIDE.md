# Testing Guide - Quiz Battle Arena

## Quick Test Checklist

### ✅ Setup Tests
- [ ] Database connection successful
- [ ] All tables created
- [ ] Sample questions inserted
- [ ] Application starts without errors

### ✅ User Authentication Tests
- [ ] User registration works
- [ ] Email validation works
- [ ] Password hashing works
- [ ] Login successful
- [ ] Session management works
- [ ] Logout works

### ✅ Quiz System Tests
- [ ] Quiz home page loads
- [ ] Matchmaking finds opponent
- [ ] Match starts successfully
- [ ] Questions display correctly
- [ ] Timer works (30 seconds)
- [ ] Answer submission works
- [ ] Correct/wrong answers highlighted
- [ ] Match completes successfully

### ✅ ELO Rating Tests
- [ ] Initial ELO is 1000
- [ ] Winner gains ELO points
- [ ] Loser loses ELO points
- [ ] ELO calculation is correct
- [ ] Higher-rated opponent = more points
- [ ] Lower-rated opponent = fewer points

### ✅ Leaderboard Tests
- [ ] Leaderboard displays correctly
- [ ] Players sorted by ELO
- [ ] Stats display correctly
- [ ] Win rate calculated correctly
- [ ] Current user highlighted

### ✅ Profile Tests
- [ ] Profile page loads
- [ ] Stats display correctly
- [ ] Avatar upload works
- [ ] Name update works
- [ ] Gallery icon works

### ✅ API Tests
- [ ] /api/player/<id> returns correct data
- [ ] /api/leaderboard returns rankings
- [ ] JSON format is correct

## Detailed Testing Steps

### 1. Setup Testing

```bash
# Run setup
python setup_database.py

# Expected output:
# ✓ Connected successfully!
# ✓ Added elo_rating column
# ✓ Added matches_played column
# ✓ Added matches_won column
# ✓ Added total_xp column
# ✓ quiz_questions table created
# ✓ matches table created
# ✓ match_answers table created
# ✓ Inserted 20 sample questions
# ✅ Database setup completed successfully!
```

### 2. User Registration Testing

1. Go to `http://localhost:5000/register`
2. Fill in the form:
   - Name: Test User 1
   - Email: test1@example.com
   - Password: Test123!
   - Confirm Password: Test123!
3. Click Register
4. Expected: Success message and redirect to login

**Test Cases:**
- Empty fields → Error message
- Invalid email → Error message
- Passwords don't match → Error message
- Duplicate email → Error message

### 3. Login Testing

1. Go to `http://localhost:5000/login`
2. Enter credentials:
   - Email: test1@example.com
   - Password: Test123!
3. Click Login
4. Expected: Redirect to Dashboard

**Test Cases:**
- Wrong password → Error message
- Non-existent email → Error message
- Empty fields → Error message

### 4. Quiz Matchmaking Testing

**Setup:** Create 2 test users

1. Login as User 1
2. Go to `/quiz`
3. Click "Find Match"
4. Expected: Match found with User 2

**Test Cases:**
- No opponents available → Error message
- Match created successfully → Redirect to match page
- Match ID is valid

### 5. Quiz Match Testing

1. Start a match
2. Verify:
   - Timer starts at 30 seconds
   - Question displays correctly
   - 4 options (A, B, C, D) display
   - Question counter shows "1 / 10"
   - Score shows "0"

3. Select an answer
4. Verify:
   - Correct answer highlighted in green
   - Wrong answer (if selected) highlighted in red
   - Score updates if correct
   - Next question loads after 2 seconds

5. Complete all 10 questions
6. Verify:
   - "Match Complete" message shows
   - Redirect to results page

**Test Cases:**
- Timer runs out → Auto-submit answer
- All questions answered → Match completes
- Score calculated correctly

### 6. Match Results Testing

1. Complete a match
2. Verify results page shows:
   - Winner/Loser/Draw status
   - Both player names
   - Both player scores
   - ELO changes (+/- values)
   - New ELO ratings
   - XP earned
   - Action buttons (Play Again, Leaderboard, Dashboard)

**Test Cases:**
- Winner has higher score
- ELO increased for winner
- ELO decreased for loser
- XP = score × 10

### 7. ELO Calculation Testing

**Test Scenario 1: Equal Ratings**
- Player 1 ELO: 1000
- Player 2 ELO: 1000
- Player 1 wins
- Expected: Player 1 ≈ +16, Player 2 ≈ -16

**Test Scenario 2: Higher Rated Wins**
- Player 1 ELO: 1200
- Player 2 ELO: 1000
- Player 1 wins
- Expected: Player 1 ≈ +11, Player 2 ≈ -11

**Test Scenario 3: Lower Rated Wins (Upset)**
- Player 1 ELO: 1000
- Player 2 ELO: 1200
- Player 1 wins
- Expected: Player 1 ≈ +21, Player 2 ≈ -21

### 8. Leaderboard Testing

1. Go to `/leaderboard`
2. Verify:
   - Players sorted by ELO (highest first)
   - Top 3 have medals (🥇🥈🥉)
   - Current user row highlighted
   - All stats display correctly
   - Win rate calculated: (wins / matches) × 100

**Test Cases:**
- Empty leaderboard → "No players yet" message
- Multiple players → Correct sorting
- Win rate calculation correct

### 9. Profile Testing

1. Go to `/profile`
2. Verify:
   - Profile hero banner displays
   - Avatar displays (or placeholder)
   - Player stats show correctly
   - Gallery icon below avatar
   - Name can be edited

3. Click gallery icon
4. Select an image
5. Verify:
   - Image uploads automatically
   - Avatar updates on page
   - Image saved in static/avatars/

**Test Cases:**
- Valid image formats (jpg, png, gif, webp)
- Invalid formats rejected
- Name update works
- Stats display correctly

### 10. API Testing

**Test /api/player/<id>**
```bash
curl http://localhost:5000/api/player/1
```

Expected response:
```json
{
  "id": 1,
  "name": "Test User",
  "elo_rating": 1016,
  "matches_played": 5,
  "matches_won": 3,
  "total_xp": 450,
  "win_rate": 60.0
}
```

**Test /api/leaderboard**
```bash
curl http://localhost:5000/api/leaderboard
```

Expected: Array of player objects sorted by ELO

### 11. Database Testing

**Verify Tables:**
```sql
SHOW TABLES;
-- Expected: users, quiz_questions, matches, match_answers

SELECT COUNT(*) FROM quiz_questions;
-- Expected: 20 (or more)

SELECT * FROM users LIMIT 5;
-- Verify columns: id, name, email, password, elo_rating, matches_played, matches_won, total_xp

SELECT * FROM matches LIMIT 5;
-- Verify match data is being saved

SELECT * FROM match_answers LIMIT 10;
-- Verify answers are being recorded
```

### 12. Performance Testing

**Load Test:**
1. Create 10 test users
2. Have them play matches simultaneously
3. Verify:
   - No database deadlocks
   - Matches complete successfully
   - ELO updates correctly
   - No duplicate matches

**Stress Test:**
1. Rapid matchmaking requests
2. Multiple concurrent matches
3. Verify system stability

### 13. Security Testing

**SQL Injection:**
- Try: `' OR '1'='1` in login fields
- Expected: No SQL injection vulnerability

**XSS Testing:**
- Try: `<script>alert('XSS')</script>` in name field
- Expected: Script tags escaped

**Session Testing:**
- Logout and try accessing /quiz
- Expected: Redirect to login

**Password Security:**
- Check database: passwords should be hashed (bcrypt)
- Not plain text

### 14. Mobile Responsiveness Testing

Test on different screen sizes:
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

Verify:
- Layout adapts correctly
- Buttons are clickable
- Text is readable
- No horizontal scrolling

### 15. Browser Compatibility Testing

Test on:
- Chrome
- Firefox
- Safari
- Edge

Verify all features work consistently.

## Automated Testing Script

Create `test_app.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

def test_api_leaderboard():
    response = requests.get(f"{BASE_URL}/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✓ Leaderboard API test passed")

def test_api_player():
    response = requests.get(f"{BASE_URL}/api/player/1")
    if response.status_code == 200:
        data = response.json()
        assert 'elo_rating' in data
        assert 'matches_played' in data
        print("✓ Player API test passed")
    else:
        print("⚠ Player not found (create a user first)")

if __name__ == '__main__':
    print("Running API tests...")
    test_api_leaderboard()
    test_api_player()
    print("\n✅ All tests passed!")
```

Run with:
```bash
python test_app.py
```

## Common Issues and Solutions

### Issue: Database connection error
**Solution:** Check MySQL is running and credentials are correct

### Issue: No opponents found
**Solution:** Create multiple test users

### Issue: Timer not working
**Solution:** Check JavaScript console for errors

### Issue: ELO not updating
**Solution:** Verify match completion endpoint is called

### Issue: Images not uploading
**Solution:** Check static/avatars folder permissions

## Test Data Cleanup

To reset test data:

```sql
-- Clear match data
DELETE FROM match_answers;
DELETE FROM matches;

-- Reset user stats
UPDATE users SET 
    elo_rating = 1000,
    matches_played = 0,
    matches_won = 0,
    total_xp = 0;

-- Or delete test users
DELETE FROM users WHERE email LIKE 'test%';
```

## Success Criteria

All tests pass when:
- ✅ Users can register and login
- ✅ Matchmaking finds opponents
- ✅ Quiz matches complete successfully
- ✅ ELO ratings update correctly
- ✅ Leaderboard displays accurately
- ✅ Profile management works
- ✅ API endpoints return correct data
- ✅ No errors in console/logs
- ✅ Mobile responsive
- ✅ Cross-browser compatible

## Reporting Issues

When reporting issues, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Error messages (if any)
5. Browser/OS information
6. Screenshots (if applicable)
