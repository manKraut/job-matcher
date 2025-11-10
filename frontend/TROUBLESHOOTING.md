# Troubleshooting: Not Seeing Changes in Browser

## Quick Fix Steps:

1. **Stop your dev server** (if running) - Press `Ctrl+C` in the terminal

2. **Clear Vite cache:**
   ```bash
   rm -rf node_modules/.vite
   ```

3. **Restart the dev server:**
   ```bash
   npm run dev
   ```

4. **Hard refresh your browser:**
   - **Mac**: `Cmd + Shift + R`
   - **Windows/Linux**: `Ctrl + Shift + R`
   - Or open DevTools (F12) → Right-click refresh button → "Empty Cache and Hard Reload"

5. **Check the correct port:**
   - Vite typically runs on `http://localhost:5173`
   - Check your terminal for the actual port number

## If Still Not Working:

- Check browser console (F12) for any errors
- Check terminal for compilation errors
- Verify all files are saved
- Try incognito/private browsing mode to rule out cache issues

