import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import axios from 'axios';
import { toast } from 'sonner';
import { BarChart3, FileText, Briefcase, Users, LogOut, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [admin, setAdmin] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [applications, setApplications] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    const adminData = localStorage.getItem('admin');
    if (!adminData) {
      navigate('/admin/login');
      return;
    }
    setAdmin(JSON.parse(adminData));
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [analyticsRes, applicationsRes, contactsRes, jobsRes] = await Promise.all([
        axios.get(`${API}/admin/analytics`),
        axios.get(`${API}/applications`),
        axios.get(`${API}/contact`),
        axios.get(`${API}/jobs`)
      ]);

      setAnalytics(analyticsRes.data);
      setApplications(applicationsRes.data);
      setContacts(contactsRes.data);
      setJobs(jobsRes.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin');
    toast.success('Logged out successfully');
    navigate('/admin/login');
  };

  const updateApplicationStatus = async (appId, status) => {
    try {
      await axios.put(`${API}/applications/${appId}/status?status=${status}`);
      toast.success('Application status updated');
      loadDashboardData();
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Failed to update status');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (!admin) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b" data-testid="admin-header">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">
                <span className="text-sky-500">Master</span>
                <span className="text-orange-500">Solis</span>
                {' '}Admin
              </h1>
              <p className="text-sm text-gray-600">Welcome back, {admin.username}</p>
            </div>
            <Button
              variant="outline"
              onClick={handleLogout}
              data-testid="logout-button"
            >
              <LogOut className="mr-2" size={18} />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8" data-testid="analytics-section">
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Contacts</p>
                  <p className="text-3xl font-bold text-sky-600" data-testid="total-contacts">
                    {analytics?.total_contacts || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-sky-100 flex items-center justify-center">
                  <Users className="text-sky-600" size={24} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Job Applications</p>
                  <p className="text-3xl font-bold text-orange-600" data-testid="total-applications">
                    {analytics?.total_applications || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
                  <Briefcase className="text-orange-600" size={24} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Active Jobs</p>
                  <p className="text-3xl font-bold text-purple-600" data-testid="total-jobs">
                    {analytics?.total_jobs || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                  <TrendingUp className="text-purple-600" size={24} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Published Blogs</p>
                  <p className="text-3xl font-bold text-emerald-600" data-testid="total-blogs">
                    {analytics?.total_blogs || 0}
                  </p>
                </div>
                <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center">
                  <FileText className="text-emerald-600" size={24} />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* AI Summary */}
        {analytics?.ai_summary && (
          <Card className="mb-8 border-sky-200 bg-sky-50">
            <CardHeader>
              <CardTitle className="flex items-center text-sky-700">
                <BarChart3 className="mr-2" size={20} />
                AI Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-700" data-testid="ai-insights">{analytics.ai_summary}</p>
            </CardContent>
          </Card>
        )}

        {/* Tabs for Data */}
        <Card className="border-0 shadow-lg">
          <CardContent className="p-6">
            <Tabs defaultValue="applications" data-testid="admin-tabs">
              <TabsList className="mb-6">
                <TabsTrigger value="applications" data-testid="applications-tab">Applications ({applications.length})</TabsTrigger>
                <TabsTrigger value="contacts" data-testid="contacts-tab">Contacts ({contacts.length})</TabsTrigger>
                <TabsTrigger value="jobs" data-testid="jobs-tab">Jobs ({jobs.length})</TabsTrigger>
              </TabsList>

              <TabsContent value="applications">
                <div className="space-y-4">
                  {applications.length === 0 ? (
                    <p className="text-center text-gray-600 py-8">No applications yet</p>
                  ) : (
                    applications.map((app, index) => (
                      <Card key={app.id} className="border" data-testid={`application-card-${index}`}>
                        <CardContent className="p-6">
                          <div className="flex flex-col md:flex-row justify-between">
                            <div className="flex-1 mb-4 md:mb-0">
                              <h3 className="text-lg font-semibold mb-2">{app.name}</h3>
                              <p className="text-sm text-gray-600 mb-1"><strong>Position:</strong> {app.job_title}</p>
                              <p className="text-sm text-gray-600 mb-1"><strong>Email:</strong> {app.email}</p>
                              <p className="text-sm text-gray-600 mb-1"><strong>Phone:</strong> {app.phone}</p>
                              <p className="text-sm text-gray-600 mb-2"><strong>Applied:</strong> {formatDate(app.applied_date)}</p>
                              {app.ai_analysis && (
                                <div className="mt-3 p-3 bg-sky-50 rounded-lg">
                                  <p className="text-xs font-semibold text-sky-700 mb-1">AI Analysis:</p>
                                  <p className="text-xs text-gray-700">{app.ai_analysis.raw_analysis}</p>
                                </div>
                              )}
                            </div>
                            <div className="flex flex-col space-y-2">
                              <Badge className={`
                                ${app.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : ''}
                                ${app.status === 'reviewing' ? 'bg-blue-100 text-blue-800' : ''}
                                ${app.status === 'shortlisted' ? 'bg-green-100 text-green-800' : ''}
                                ${app.status === 'rejected' ? 'bg-red-100 text-red-800' : ''}
                              `}>
                                {app.status}
                              </Badge>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateApplicationStatus(app.id, 'reviewing')}
                                disabled={app.status === 'reviewing'}
                              >
                                Mark Reviewing
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600"
                                onClick={() => updateApplicationStatus(app.id, 'shortlisted')}
                                disabled={app.status === 'shortlisted'}
                              >
                                Shortlist
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </TabsContent>

              <TabsContent value="contacts">
                <div className="space-y-4">
                  {contacts.length === 0 ? (
                    <p className="text-center text-gray-600 py-8">No contacts yet</p>
                  ) : (
                    contacts.map((contact, index) => (
                      <Card key={contact.id} className="border" data-testid={`contact-card-${index}`}>
                        <CardContent className="p-6">
                          <h3 className="text-lg font-semibold mb-2">{contact.name}</h3>
                          <p className="text-sm text-gray-600 mb-1"><strong>Email:</strong> {contact.email}</p>
                          {contact.subject && (
                            <p className="text-sm text-gray-600 mb-1"><strong>Subject:</strong> {contact.subject}</p>
                          )}
                          <p className="text-sm text-gray-600 mb-2"><strong>Date:</strong> {formatDate(contact.timestamp)}</p>
                          <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{contact.message}</p>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </TabsContent>

              <TabsContent value="jobs">
                <div className="space-y-4">
                  {jobs.length === 0 ? (
                    <p className="text-center text-gray-600 py-8">No jobs posted yet</p>
                  ) : (
                    jobs.map((job, index) => (
                      <Card key={job.id} className="border" data-testid={`job-card-${index}`}>
                        <CardContent className="p-6">
                          <div className="flex justify-between items-start mb-3">
                            <h3 className="text-lg font-semibold">{job.title}</h3>
                            <Badge className={job.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                              {job.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-1"><strong>Department:</strong> {job.department}</p>
                          <p className="text-sm text-gray-600 mb-1"><strong>Location:</strong> {job.location}</p>
                          <p className="text-sm text-gray-600 mb-1"><strong>Type:</strong> {job.type}</p>
                          <p className="text-sm text-gray-600"><strong>Posted:</strong> {formatDate(job.posted_date)}</p>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;