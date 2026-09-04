import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://wcksscwgeoysnqiluxoh.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indja3NzY3dnZW95c25xaWx1eG9oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUyMDQ3NzAsImV4cCI6MjEwMDc4MDc3MH0.pkS0lo2a4GGS-wDtwFzQwKMeVF-It6sPMrgooPyU-Do';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
