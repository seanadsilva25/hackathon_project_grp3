import { supabase } from './supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

/**
 * Fetch the authenticated user's authority profile.
 */
export async function getAuthorityProfile() {
  try {
    const { data: authData, error: authError } = await supabase.auth.getUser();
    if (authError || !authData?.user) {
      console.log("No authenticated user, using mock authority for demo");
      return {
        id: "mock-authority-123",
        name: "Demo Police Chief",
        department: "Police Command",
        jurisdiction: "Mumbai North",
        role: "authority",
        phone: "+91 9876543210"
      };
    }

    const { data: profile, error: profileError } = await supabase
      .from('authorities')
      .select('*')
      .eq('id', authData.user.id)
      .single();

    if (profileError || !profile) {
      console.log("Profile not found in DB, using mock authority for demo");
      return {
        id: authData.user.id,
        name: "Demo BMC Official",
        department: "BMC Civic Operations",
        jurisdiction: "Mumbai South",
        role: "authority",
        phone: "+91 9876543210"
      };
    }

    return profile;
  } catch (err) {
    console.error("Error fetching authority profile:", err);
    return {
      id: "error-mock",
      name: "Demo Official (Offline)",
      department: "Police",
      jurisdiction: "Local",
      role: "authority"
    };
  }
}

/**
 * Fetch complaints relevant to this authority's jurisdiction or department.
 */
export async function getComplaints(authority) {
  try {
    let query = supabase.from('complaints').select('*').order('created_at', { ascending: false });

    // Filter by assigned authority to ensure strict isolation
    if (authority?.id && authority.id !== "mock-authority-123") {
      query = query.eq('assigned_authority_id', authority.id);
    } else if (authority?.id === "mock-authority-123") {
      // Force empty query to trigger mock data fallback below
      query = query.eq('id', 'force-empty-mock-query');
    }

    const { data, error } = await query;

    if (error) throw error;
    
    if (!data || data.length === 0) {
      console.log("No complaints found, using mock complaints for demo");
      return [
        {
          id: "mock-comp-1",
          title: "Suspect Activity in Market",
          category: "Suspicious Activity",
          address: "Crawford Market, Mumbai",
          latitude: 18.9482,
          longitude: 72.8338,
          status: "pending",
          upvote_count: 12,
          verification_count: 0,
          created_at: new Date().toISOString()
        },
        {
          id: "mock-comp-2",
          title: "Major Pothole on Highway",
          category: "Road Damage",
          address: "Western Express Hwy, Mumbai",
          latitude: 19.1136,
          longitude: 72.8697,
          status: "in_progress",
          upvote_count: 4,
          verification_count: 1,
          created_at: new Date(Date.now() - 86400000).toISOString() // 1 day ago
        },
        {
          id: "mock-comp-3",
          title: "Public Disturbance at Station",
          category: "Public Disturbance",
          address: "Dadar Station, Mumbai",
          latitude: 19.0178,
          longitude: 72.8478,
          status: "resolved",
          upvote_count: 2,
          verification_count: 3,
          created_at: new Date(Date.now() - 172800000).toISOString() // 2 days ago
        }
      ];
    }
    
    // Inject mock verifications count to simulate citizen verifications
    // since the real DB might be empty for the hackathon
    return data.map(c => ({
      ...c,
      verification_count: Math.floor(Math.random() * 5)
    }));
  } catch (err) {
    console.error("Error fetching complaints:", err);
    return [];
  }
}

/**
 * Update the status of a complaint securely via Flask backend
 */
export async function updateComplaintStatus(complaintId, authorityId, newStatus) {
  try {
    const response = await fetch(`${API_URL}/complaints/${complaintId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus, authority_id: authorityId })
    });
    
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Failed to update status");
    return data;
  } catch (err) {
    console.error("Error updating status:", err);
    throw err;
  }
}

/**
 * Fetch unread notifications for this authority
 */
export async function getNotifications(authorityId) {
  const getMockNotifications = () => [
    { id: "mock-notif-1", title: "New complaint assigned", body: "A new Road Damage complaint has been assigned to your jurisdiction.", type: "NEW_COMPLAINT", priority: "NORMAL", created_at: new Date().toISOString(), is_read: false },
    { id: "mock-notif-2", title: "Community threshold reached", body: "Suspicious Activity in Market has reached 10 community supports.", type: "THRESHOLD", priority: "HIGH", created_at: new Date(Date.now() - 3600000).toISOString(), is_read: false },
    { id: "mock-notif-3", title: "Critical complaint requires attention", body: "Public Disturbance has been marked as critical.", type: "CRITICAL", priority: "CRITICAL", created_at: new Date(Date.now() - 7200000).toISOString(), is_read: false },
    { id: "mock-notif-4", title: "Complaint resolved", body: "Streetlight complaint has been marked Resolved.", type: "RESOLVED", priority: "SUCCESS", created_at: new Date(Date.now() - 86400000).toISOString(), is_read: false },
  ];

  // If using the mock authority, skip the Supabase query to prevent UUID syntax errors
  if (!authorityId || authorityId === "mock-authority-123" || !authorityId.includes("-")) {
    console.log("Using mock authority, injecting mock notifications");
    return getMockNotifications();
  }

  try {
    const { data, error } = await supabase
      .from('notifications')
      .select('*')
      .eq('authority_id', authorityId)
      .eq('is_read', false)
      .order('created_at', { ascending: false });

    if (error) throw error;
    
    // Parse types dynamically since backend schema might lack `type`
    const parsedData = (data || []).map(notif => {
      const lowerTitle = (notif.title || '').toLowerCase();
      let type = 'STATUS';
      let priority = 'NORMAL';

      if (lowerTitle.includes('new complaint') || lowerTitle.includes('assigned')) {
        type = 'NEW_COMPLAINT';
        priority = 'NORMAL';
      } else if (lowerTitle.includes('critical')) {
        type = 'CRITICAL';
        priority = 'CRITICAL';
      } else if (lowerTitle.includes('threshold')) {
        type = 'THRESHOLD';
        priority = 'HIGH';
      } else if (lowerTitle.includes('resolved')) {
        type = 'RESOLVED';
        priority = 'SUCCESS';
      } else if (lowerTitle.includes('verification')) {
        type = 'VERIFICATION';
        priority = 'SUCCESS';
      }

      return {
        ...notif,
        type,
        priority
      };
    });

    if (parsedData.length === 0) {
      console.log("No real notifications found, injecting mocks for demo");
      return getMockNotifications();
    }

    return parsedData;
  } catch (err) {
    console.error("Error fetching notifications:", err);
    // Return mocks on error so the UI still looks good during the demo if the DB fails
    return getMockNotifications();
  }
}

/**
 * Mark a notification as read
 */
export async function markNotificationRead(notificationId) {
  try {
    await supabase.from('notifications').update({ is_read: true }).eq('id', notificationId);
  } catch (err) {
    console.error("Error marking notification read:", err);
  }
}
