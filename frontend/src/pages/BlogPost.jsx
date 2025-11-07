import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import axios from 'axios';
import { Calendar, User, ArrowLeft, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BlogPost = () => {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [summary, setSummary] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    loadPost();
  }, [slug]);

  const loadPost = async () => {
    try {
      const response = await axios.get(`${API}/blog/${slug}`);
      setPost(response.data);
    } catch (error) {
      console.error('Error loading blog post:', error);
      toast.error('Blog post not found');
    }
  };

  const generateSummary = async () => {
    setLoadingSummary(true);
    try {
      const response = await axios.post(`${API}/blog/${slug}/summarize`);
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error generating summary:', error);
      toast.error('Failed to generate summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (!post) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="flex items-center justify-center h-screen">
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Post Header */}
      <section className="pt-32 pb-12 px-4 bg-gradient-to-br from-sky-50 via-white to-orange-50" data-testid="blog-post-header">
        <div className="max-w-4xl mx-auto">
          <Link
            to="/blog"
            className="inline-flex items-center text-sky-600 hover:text-sky-700 mb-8"
            data-testid="back-to-blog-link"
          >
            <ArrowLeft className="mr-2" size={20} />
            Back to Blog
          </Link>
          <div className="flex flex-wrap gap-2 mb-4">
            {post.tags && post.tags.map((tag, i) => (
              <Badge key={i} variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-6" data-testid="blog-post-title">{post.title}</h1>
          <div className="flex items-center gap-6 text-gray-600">
            <div className="flex items-center">
              <User size={18} className="mr-2" />
              <span>{post.author}</span>
            </div>
            <div className="flex items-center">
              <Calendar size={18} className="mr-2" />
              <span>{formatDate(post.created_date)}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Post Content */}
      <section className="py-12 px-4 bg-white" data-testid="blog-post-content-section">
        <div className="max-w-4xl mx-auto">
          {post.featured_image && (
            <div className="mb-12 rounded-2xl overflow-hidden shadow-xl">
              <img
                src={post.featured_image}
                alt={post.title}
                className="w-full h-96 object-cover"
              />
            </div>
          )}

          {/* AI Summary Section */}
          <Card className="mb-12 border-sky-200 bg-sky-50">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center">
                  <Sparkles className="mr-2 text-sky-600" size={20} />
                  AI-Generated Summary
                </h3>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={generateSummary}
                  disabled={loadingSummary}
                  data-testid="generate-summary-button"
                >
                  {loadingSummary ? 'Generating...' : summary ? 'Regenerate' : 'Generate'}
                </Button>
              </div>
              {summary ? (
                <div className="text-sm text-gray-700 whitespace-pre-wrap" data-testid="ai-summary-content">
                  {summary}
                </div>
              ) : (
                <p className="text-sm text-gray-600">Click the button above to generate an AI summary of this post.</p>
              )}
            </CardContent>
          </Card>

          <div className="prose prose-lg max-w-none" data-testid="blog-post-body">
            {post.content.split('\n').map((paragraph, index) => (
              paragraph.trim() && <p key={index} className="mb-4 text-base text-gray-700">{paragraph}</p>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default BlogPost;