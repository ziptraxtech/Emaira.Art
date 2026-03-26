import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTranslation } from "react-i18next";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Textarea } from "@/components/ui/textarea";
import { 
  ArrowLeft, 
  Play, 
  Clock, 
  MapPin, 
  Calendar,
  Fingerprint,
  Palette,
  FileSignature,
  Grid3X3,
  Lock,
  Check,
  User,
  Menu,
  X,
  LogOut,
  Share2,
  Star,
  ThumbsUp,
  MessageSquare,
  Twitter,
  Facebook,
  Linkedin,
  Link as LinkIcon,
  Copy
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

const StoryDetail = () => {
  const { storyId } = useParams();
  const { user, login, logout } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [story, setStory] = useState(null);
  const [artwork, setArtwork] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Reviews state
  const [reviews, setReviews] = useState([]);
  const [averageRating, setAverageRating] = useState(0);
  const [totalReviews, setTotalReviews] = useState(0);
  const [showReviewDialog, setShowReviewDialog] = useState(false);
  const [newReview, setNewReview] = useState({ rating: 5, title: "", comment: "" });
  const [submittingReview, setSubmittingReview] = useState(false);
  
  // Share state
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [shareData, setShareData] = useState(null);

  useEffect(() => {
    fetchStoryAndArtwork();
  }, [storyId]);

  const fetchStoryAndArtwork = async () => {
    try {
      const storyResponse = await axios.get(`${API}/stories/${storyId}`, {
        withCredentials: true
      });
      setStory(storyResponse.data);

      if (storyResponse.data.artwork_id) {
        const artworkResponse = await axios.get(`${API}/artworks/${storyResponse.data.artwork_id}`);
        setArtwork(artworkResponse.data);
      }
    } catch (error) {
      console.error("Error fetching story:", error);
      toast.error("Failed to load story");
    } finally {
      setLoading(false);
    }
  };

  // Fetch reviews
  useEffect(() => {
    if (storyId) {
      fetchReviews();
    }
  }, [storyId]);

  const fetchReviews = async () => {
    try {
      const res = await axios.get(`${API}/reviews/story/${storyId}`);
      setReviews(res.data.reviews || []);
      setAverageRating(res.data.average_rating || 0);
      setTotalReviews(res.data.total_reviews || 0);
    } catch (error) {
      console.error("Error fetching reviews:", error);
    }
  };

  const submitReview = async () => {
    if (!user) {
      login();
      return;
    }
    
    setSubmittingReview(true);
    try {
      await axios.post(`${API}/reviews/`, {
        target_type: "story",
        target_id: storyId,
        rating: newReview.rating,
        title: newReview.title,
        comment: newReview.comment
      }, { withCredentials: true });
      
      toast.success("Review submitted successfully!");
      setShowReviewDialog(false);
      setNewReview({ rating: 5, title: "", comment: "" });
      fetchReviews();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to submit review");
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleShare = async (platform) => {
    try {
      const res = await axios.post(`${API}/share/story/${storyId}`, { platform }, { withCredentials: true });
      setShareData(res.data);
      
      const shareUrl = res.data.share_url;
      const title = res.data.og_metadata?.title || story?.title;
      
      if (platform === 'copy') {
        navigator.clipboard.writeText(shareUrl);
        toast.success(t('common.linkCopied'));
      } else if (platform === 'twitter') {
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(shareUrl)}`, '_blank');
      } else if (platform === 'facebook') {
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`, '_blank');
      } else if (platform === 'linkedin') {
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`, '_blank');
      } else if (platform === 'native' && navigator.share) {
        await navigator.share({
          title: title,
          text: res.data.og_metadata?.description,
          url: shareUrl
        });
      }
    } catch (error) {
      console.error("Share error:", error);
    }
  };

  const markHelpful = async (reviewId) => {
    if (!user) {
      login();
      return;
    }
    try {
      await axios.post(`${API}/reviews/${reviewId}/helpful`, {}, { withCredentials: true });
      toast.success("Marked as helpful");
      fetchReviews();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Already marked");
    }
  };

  const handlePurchase = async (accessType) => {
    if (!user) {
      login();
      return;
    }

    setPurchasing(true);
    try {
      const response = await axios.post(
        `${API}/payments/stripe/checkout`,
        {
          story_id: storyId,
          access_type: accessType,
          origin_url: window.location.origin
        },
        { withCredentials: true }
      );

      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error("Payment error:", error);
      toast.error("Failed to initiate payment");
    } finally {
      setPurchasing(false);
    }
  };

  const handleStartExperience = () => {
    if (!user) {
      login();
      return;
    }
    navigate(`/experience/${storyId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#A8A8A0]">Loading story...</p>
        </div>
      </div>
    );
  }

  if (!story || !artwork) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#A8A8A0] mb-4">Story not found</p>
          <Button onClick={() => navigate('/gallery')} className="btn-gold">
            Back to Gallery
          </Button>
        </div>
      </div>
    );
  }

  const hasAccess = story.has_access;

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-[#050505] text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#F5F5F0] hidden sm:block">Emaira.Art</span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              <Link to="/gallery" className="nav-link text-sm font-medium">Gallery</Link>
              <Link to="/pricing" className="nav-link text-sm font-medium">Pricing</Link>
              {user && <Link to="/dashboard" className="nav-link text-sm font-medium">Dashboard</Link>}
            </div>

            <div className="hidden md:flex items-center gap-4">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 text-[#F5F5F0]">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-[#0a0a0a] border-[#1a1a1a]">
                    <DropdownMenuItem onClick={() => navigate('/dashboard')} className="text-[#F5F5F0] focus:bg-[#111] cursor-pointer">
                      <User className="w-4 h-4 mr-2" /> Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout} className="text-[#F5F5F0] focus:bg-[#111] cursor-pointer">
                      <LogOut className="w-4 h-4 mr-2" /> Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button onClick={login} className="btn-gold text-sm">Sign In</Button>
              )}
            </div>

            <button className="md:hidden text-[#F5F5F0]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative min-h-[60vh] flex items-end">
        <div className="absolute inset-0">
          <img 
            src={artwork.image_url}
            alt={artwork.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-[#050505]/70 to-transparent"></div>
        </div>

        <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 pt-32">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/gallery')} 
            className="text-[#A8A8A0] hover:text-[#F5F5F0] mb-6 -ml-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Gallery
          </Button>

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge className="badge-gold">{artwork.period}</Badge>
            <Badge className="badge-forensic">
              <Fingerprint className="w-3 h-3 mr-1" /> AI Forensics
            </Badge>
          </div>

          <h1 className="font-display text-4xl lg:text-5xl xl:text-6xl text-[#F5F5F0] mb-4" data-testid="story-title">
            {story.title}
          </h1>

          <div className="flex flex-wrap items-center gap-4 text-[#A8A8A0] mb-6">
            <span className="flex items-center gap-2">
              <Calendar className="w-4 h-4" /> {artwork.year}
            </span>
            <span className="flex items-center gap-2">
              <MapPin className="w-4 h-4" /> {artwork.location}
            </span>
            <span className="flex items-center gap-2">
              <Clock className="w-4 h-4" /> {story.duration_minutes} min experience
            </span>
          </div>

          <p className="text-lg text-[#A8A8A0] max-w-2xl">
            {story.description}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Artwork Details */}
            <div className="card-obsidian rounded-lg p-6">
              <h2 className="font-display text-2xl text-[#F5F5F0] mb-4">About the Artwork</h2>
              <div className="grid sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-[#666660]">Artist</span>
                  <p className="text-[#F5F5F0]">{artwork.artist}</p>
                </div>
                <div>
                  <span className="text-[#666660]">Year</span>
                  <p className="text-[#F5F5F0]">{artwork.year}</p>
                </div>
                <div>
                  <span className="text-[#666660]">Medium</span>
                  <p className="text-[#F5F5F0]">{artwork.medium}</p>
                </div>
                <div>
                  <span className="text-[#666660]">Dimensions</span>
                  <p className="text-[#F5F5F0]">{artwork.dimensions}</p>
                </div>
              </div>
              <p className="text-[#A8A8A0] mt-4">{artwork.description}</p>
            </div>

            {/* Provenance */}
            {artwork.provenance && artwork.provenance.length > 0 && (
              <div className="card-obsidian rounded-lg p-6">
                <h2 className="font-display text-2xl text-[#F5F5F0] mb-4">Provenance</h2>
                <div className="space-y-4">
                  {artwork.provenance.map((item, index) => (
                    <div key={index} className="flex gap-4">
                      <div className="w-16 text-[#D4AF37] font-mono text-sm">{item.year}</div>
                      <div className="flex-1 text-[#A8A8A0]">{item.event}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Forensic Features Preview */}
            <div className="card-obsidian rounded-lg p-6">
              <h2 className="font-display text-2xl text-[#F5F5F0] mb-4">
                Forensic Analysis Features
              </h2>
              <div className="grid sm:grid-cols-3 gap-4">
                <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <Palette className="w-8 h-8 text-[#00F0FF] mb-3" />
                  <h3 className="font-display text-[#F5F5F0] mb-1">Pigment Mapping</h3>
                  <p className="text-xs text-[#A8A8A0]">Chemical composition analysis</p>
                </div>
                <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <FileSignature className="w-8 h-8 text-[#00F0FF] mb-3" />
                  <h3 className="font-display text-[#F5F5F0] mb-1">Signature Auth</h3>
                  <p className="text-xs text-[#A8A8A0]">Comparative overlays</p>
                </div>
                <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <Grid3X3 className="w-8 h-8 text-[#00F0FF] mb-3" />
                  <h3 className="font-display text-[#F5F5F0] mb-1">Canvas Analysis</h3>
                  <p className="text-xs text-[#A8A8A0]">Weave density mapping</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar - Purchase Options */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-4">
              {hasAccess ? (
                <div className="card-obsidian rounded-lg p-6 border-[#D4AF37]">
                  <div className="flex items-center gap-2 text-[#D4AF37] mb-4">
                    <Check className="w-5 h-5" />
                    <span className="font-medium">Access Granted</span>
                  </div>
                  <Button 
                    onClick={handleStartExperience}
                    className="w-full btn-gold text-base"
                    data-testid="start-experience-btn"
                  >
                    <Play className="w-4 h-4 mr-2" /> Start Experience
                  </Button>
                </div>
              ) : (
                <>
                  {/* Narrative Only */}
                  <div className="card-obsidian rounded-lg p-6">
                    <h3 className="font-display text-xl text-[#F5F5F0] mb-2">The Short Story</h3>
                    <p className="text-sm text-[#A8A8A0] mb-4">
                      3-minute narrative VR experience through the artwork's history
                    </p>
                    <div className="flex items-baseline gap-1 mb-4">
                      <span className="text-3xl font-display text-[#D4AF37]">${story.price_narrative}</span>
                      <span className="text-[#666660]">/ story</span>
                    </div>
                    <ul className="space-y-2 mb-6 text-sm text-[#A8A8A0]">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#D4AF37]" /> Full narrative experience
                      </li>
                      <li className="flex items-center gap-2">
                        <Lock className="w-4 h-4 text-[#666660]" /> Forensic view locked
                      </li>
                    </ul>
                    <Button 
                      onClick={() => handlePurchase("narrative")}
                      disabled={purchasing}
                      className="w-full btn-outline-gold"
                      data-testid="buy-narrative-btn"
                    >
                      {purchasing ? "Processing..." : "Get Narrative Access"}
                    </Button>
                  </div>

                  {/* Deep Dive */}
                  <div className="card-obsidian rounded-lg p-6 border-[#D4AF37] relative overflow-hidden">
                    <div className="absolute top-0 right-0 bg-[#D4AF37] text-[#050505] text-xs font-bold px-3 py-1">
                      RECOMMENDED
                    </div>
                    <h3 className="font-display text-xl text-[#F5F5F0] mb-2">The Deep Dive</h3>
                    <p className="text-sm text-[#A8A8A0] mb-4">
                      Complete experience with AI forensic analysis
                    </p>
                    <div className="flex items-baseline gap-1 mb-4">
                      <span className="text-3xl font-display text-[#D4AF37]">${story.price_full}</span>
                      <span className="text-[#666660]">/ story</span>
                    </div>
                    <ul className="space-y-2 mb-6 text-sm text-[#A8A8A0]">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#D4AF37]" /> Full narrative experience
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#00F0FF]" /> Complete forensic view
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#00F0FF]" /> AI pigment analysis
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#00F0FF]" /> Signature authentication
                      </li>
                    </ul>
                    <Button 
                      onClick={() => handlePurchase("full")}
                      disabled={purchasing}
                      className="w-full btn-gold"
                      data-testid="buy-full-btn"
                    >
                      {purchasing ? "Processing..." : "Get Full Access"}
                    </Button>
                  </div>

                  {/* Subscription Upsell */}
                  <div className="glass-gold rounded-lg p-4 text-center">
                    <p className="text-sm text-[#D4AF37] mb-2">Want unlimited access?</p>
                    <Button 
                      onClick={() => navigate('/pricing')}
                      variant="link"
                      className="text-[#F5F5F0] hover:text-[#D4AF37]"
                    >
                      View Subscription Plans →
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>
          
          {/* Reviews Section */}
          <div className="mt-12">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <h2 className="font-display text-2xl text-[#F5F5F0]">Reviews</h2>
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`w-5 h-5 ${star <= averageRating ? 'text-[#D4AF37] fill-[#D4AF37]' : 'text-[#333]'}`}
                      />
                    ))}
                  </div>
                  <span className="text-[#A8A8A0]">
                    {averageRating > 0 ? `${averageRating} (${totalReviews} reviews)` : 'No reviews yet'}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => setShowShareDialog(true)}
                  variant="outline"
                  className="border-[#333] text-[#A8A8A0] hover:text-[#F5F5F0]"
                  data-testid="share-btn"
                >
                  <Share2 className="w-4 h-4 mr-2" /> Share
                </Button>
                <Button
                  onClick={() => setShowReviewDialog(true)}
                  className="btn-gold"
                  data-testid="write-review-btn"
                >
                  <MessageSquare className="w-4 h-4 mr-2" /> Write Review
                </Button>
              </div>
            </div>
            
            {reviews.length === 0 ? (
              <div className="card-obsidian rounded-lg p-8 text-center">
                <MessageSquare className="w-12 h-12 mx-auto text-[#333] mb-4" />
                <p className="text-[#A8A8A0]">No reviews yet. Be the first to review this story!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {reviews.slice(0, 5).map((review) => (
                  <div key={review.review_id} className="card-obsidian rounded-lg p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {review.user_picture ? (
                          <img src={review.user_picture} alt={review.user_name} className="w-10 h-10 rounded-full" />
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-[#1a1a1a] flex items-center justify-center">
                            <User className="w-5 h-5 text-[#666]" />
                          </div>
                        )}
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-[#F5F5F0]">{review.user_name}</p>
                            {review.is_verified_purchase && (
                              <Badge className="bg-green-900/30 text-green-400 text-xs">Verified</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="flex">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`w-3 h-3 ${star <= review.rating ? 'text-[#D4AF37] fill-[#D4AF37]' : 'text-[#333]'}`}
                                />
                              ))}
                            </div>
                            <span className="text-xs text-[#666]">
                              {new Date(review.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    {review.title && (
                      <h4 className="font-medium text-[#F5F5F0] mb-2">{review.title}</h4>
                    )}
                    {review.comment && (
                      <p className="text-[#A8A8A0] text-sm">{review.comment}</p>
                    )}
                    <div className="flex items-center gap-4 mt-4">
                      <button
                        onClick={() => markHelpful(review.review_id)}
                        className="flex items-center gap-1 text-xs text-[#666] hover:text-[#A8A8A0]"
                      >
                        <ThumbsUp className="w-4 h-4" /> Helpful ({review.helpful_count || 0})
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Review Dialog */}
      <Dialog open={showReviewDialog} onOpenChange={setShowReviewDialog}>
        <DialogContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0]">
          <DialogHeader>
            <DialogTitle className="font-display text-xl">Write a Review</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-[#A8A8A0]">Rating</label>
              <div className="flex gap-2 mt-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setNewReview({ ...newReview, rating: star })}
                    className="focus:outline-none"
                  >
                    <Star
                      className={`w-8 h-8 transition-colors ${
                        star <= newReview.rating 
                          ? 'text-[#D4AF37] fill-[#D4AF37]' 
                          : 'text-[#333] hover:text-[#D4AF37]'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm text-[#A8A8A0]">Title (optional)</label>
              <input
                type="text"
                value={newReview.title}
                onChange={(e) => setNewReview({ ...newReview, title: e.target.value })}
                placeholder="Summarize your experience"
                className="w-full mt-1 px-3 py-2 bg-[#111] border border-[#1a1a1a] rounded-lg text-[#F5F5F0] focus:border-[#D4AF37] focus:outline-none"
              />
            </div>
            <div>
              <label className="text-sm text-[#A8A8A0]">Your Review</label>
              <Textarea
                value={newReview.comment}
                onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
                placeholder="Share your thoughts about this VR experience..."
                className="w-full mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0] min-h-[120px]"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowReviewDialog(false)} className="border-[#333] text-[#A8A8A0]">
              Cancel
            </Button>
            <Button onClick={submitReview} disabled={submittingReview} className="btn-gold">
              {submittingReview ? "Submitting..." : "Submit Review"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      {/* Share Dialog */}
      <Dialog open={showShareDialog} onOpenChange={setShowShareDialog}>
        <DialogContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0]">
          <DialogHeader>
            <DialogTitle className="font-display text-xl">Share This Story</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-[#A8A8A0]">
              Share "{story?.title}" with your friends and followers
            </p>
            <div className="grid grid-cols-2 gap-3">
              <Button
                onClick={() => handleShare('twitter')}
                variant="outline"
                className="border-[#333] text-[#A8A8A0] hover:bg-[#1DA1F2]/20 hover:border-[#1DA1F2] hover:text-[#1DA1F2]"
              >
                <Twitter className="w-4 h-4 mr-2" /> Twitter
              </Button>
              <Button
                onClick={() => handleShare('facebook')}
                variant="outline"
                className="border-[#333] text-[#A8A8A0] hover:bg-[#4267B2]/20 hover:border-[#4267B2] hover:text-[#4267B2]"
              >
                <Facebook className="w-4 h-4 mr-2" /> Facebook
              </Button>
              <Button
                onClick={() => handleShare('linkedin')}
                variant="outline"
                className="border-[#333] text-[#A8A8A0] hover:bg-[#0A66C2]/20 hover:border-[#0A66C2] hover:text-[#0A66C2]"
              >
                <Linkedin className="w-4 h-4 mr-2" /> LinkedIn
              </Button>
              <Button
                onClick={() => handleShare('copy')}
                variant="outline"
                className="border-[#333] text-[#A8A8A0] hover:bg-[#D4AF37]/20 hover:border-[#D4AF37] hover:text-[#D4AF37]"
              >
                <Copy className="w-4 h-4 mr-2" /> Copy Link
              </Button>
            </div>
            {navigator.share && (
              <Button
                onClick={() => handleShare('native')}
                className="w-full btn-gold"
              >
                <Share2 className="w-4 h-4 mr-2" /> Share via Device
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default StoryDetail;
