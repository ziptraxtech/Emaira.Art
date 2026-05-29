import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "@/components/ui/calendar";
import Footer from "@/components/Footer";
import {
  ArrowLeft,
  CalendarDays,
  MapPin,
  Clock,
  Users,
  Sparkles,
  Video,
  Building,
  Globe,
  User,
  Menu,
  X,
  LogOut,
  ExternalLink
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Events = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());

  const upcomingEvents = [
    {
      id: 1,
      title: "VR Exhibition: Renaissance Masters",
      type: "Virtual",
      date: "Feb 28, 2026",
      time: "6:00 PM EST",
      location: "Online - VR Headset Required",
      description: "Journey through the studios of Leonardo, Michelangelo, and Raphael in an immersive VR experience.",
      attendees: 234,
      featured: true,
      image: "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400"
    },
    {
      id: 2,
      title: "Authentication Workshop: Detecting Forgeries",
      type: "Hybrid",
      date: "Mar 5, 2026",
      time: "2:00 PM EST",
      location: "MoMA, New York + Virtual",
      description: "Learn forensic techniques used by experts to identify fake artworks.",
      attendees: 156,
      featured: true,
      image: "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=400"
    },
    {
      id: 3,
      title: "Collector's Circle: Private Viewing",
      type: "In-Person",
      date: "Mar 12, 2026",
      time: "7:00 PM GMT",
      location: "Tate Modern, London",
      description: "Exclusive viewing for Pro Collector subscribers featuring newly authenticated works.",
      attendees: 48,
      featured: false,
      image: "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400"
    },
    {
      id: 4,
      title: "Webinar: The Future of Art Authentication",
      type: "Virtual",
      date: "Mar 18, 2026",
      time: "11:00 AM EST",
      location: "Online",
      description: "Panel discussion with leading art historians and AI researchers.",
      attendees: 892,
      featured: false,
      image: "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400"
    }
  ];

  const pastEvents = [
    {
      title: "Van Gogh: Beyond the Canvas",
      date: "Jan 15, 2026",
      attendees: 1240,
      recording: true
    },
    {
      title: "Pigment Analysis Masterclass",
      date: "Jan 8, 2026",
      attendees: 345,
      recording: true
    },
    {
      title: "Art Market Trends 2026",
      date: "Dec 20, 2025",
      attendees: 567,
      recording: false
    }
  ];

  const getEventTypeIcon = (type) => {
    switch (type) {
      case "Virtual": return <Video className="w-4 h-4" />;
      case "In-Person": return <Building className="w-4 h-4" />;
      case "Hybrid": return <Globe className="w-4 h-4" />;
      default: return <CalendarDays className="w-4 h-4" />;
    }
  };

  const getEventTypeColor = (type) => {
    switch (type) {
      case "Virtual": return "bg-[#1A365D]/10 text-[#1A365D]";
      case "In-Person": return "bg-[#2D5A47]/10 text-[#2D5A47]";
      case "Hybrid": return "bg-[#B8962F]/10 text-[#B8962F]";
      default: return "bg-[#8A8A80]/10 text-[#8A8A80]";
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link to="/" className="flex items-center gap-2" data-testid="logo">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-white text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#1A1A18] hidden sm:block">Emaira.Art</span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              <Link to="/gallery" className="nav-link text-sm font-medium">Gallery</Link>
              <Link to="/about" className="nav-link text-sm font-medium">About</Link>
              <Link to="/technology" className="nav-link text-sm font-medium">Technology</Link>
              <Link to="/events" className="text-sm font-medium text-[#B8962F]">Events</Link>
              <Link to="/pricing" className="nav-link text-sm font-medium">Pricing</Link>
            </div>

            <div className="hidden md:flex items-center gap-4">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 text-[#1A1A18]">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-white border-[#E8E8E0]">
                    <DropdownMenuItem onClick={() => navigate('/dashboard')} className="cursor-pointer">
                      <User className="w-4 h-4 mr-2" /> Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout} className="cursor-pointer">
                      <LogOut className="w-4 h-4 mr-2" /> Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button onClick={login} className="btn-gold text-sm">Sign In</Button>
              )}
            </div>

            <button className="md:hidden text-[#1A1A18]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-16 hero-gradient">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/')} 
            className="text-[#4A4A45] hover:text-[#1A1A18] mb-6 -ml-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
          </Button>

          <div className="max-w-3xl">
            <Badge className="badge-gold mb-4">
              <CalendarDays className="w-3 h-3 mr-1" /> Events & Exhibitions
            </Badge>
            <h1 className="font-display text-4xl lg:text-5xl text-[#1A1A18] mb-6">
              Experience Art
              <span className="block text-gold-gradient">In New Ways</span>
            </h1>
            <p className="text-lg text-[#4A4A45] leading-relaxed">
              Join our virtual exhibitions, workshops, and exclusive events. 
              Connect with fellow art enthusiasts and learn from world-renowned experts.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Events */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <Badge className="badge-forensic mb-2">
                <Sparkles className="w-3 h-3 mr-1" /> Featured
              </Badge>
              <h2 className="font-display text-2xl text-[#1A1A18]">Upcoming Events</h2>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {upcomingEvents.filter(e => e.featured).map((event) => (
              <div key={event.id} className="card-ivory rounded-lg overflow-hidden group" data-testid={`event-${event.id}`}>
                <div className="relative h-48">
                  <img 
                    src={event.image}
                    alt={event.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute top-4 left-4">
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${getEventTypeColor(event.type)}`}>
                      {getEventTypeIcon(event.type)}
                      {event.type}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="font-display text-xl text-[#1A1A18] mb-2 group-hover:text-[#B8962F] transition-colors">
                    {event.title}
                  </h3>
                  <p className="text-sm text-[#4A4A45] mb-4">{event.description}</p>
                  <div className="flex flex-wrap gap-4 text-sm text-[#8A8A80] mb-4">
                    <span className="flex items-center gap-1">
                      <CalendarDays className="w-4 h-4" /> {event.date}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" /> {event.time}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-4 h-4" /> {event.attendees} registered
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-[#4A4A45] mb-4">
                    <MapPin className="w-4 h-4 text-[#B8962F]" />
                    {event.location}
                  </div>
                  <Button className="w-full btn-gold">Register Now</Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* All Events + Calendar */}
      <section className="py-16 bg-[#F5F5F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Events List */}
            <div className="lg:col-span-2">
              <h2 className="font-display text-2xl text-[#1A1A18] mb-6">All Upcoming Events</h2>
              <div className="space-y-4">
                {upcomingEvents.map((event) => (
                  <div key={event.id} className="card-ivory rounded-lg p-4 flex gap-4 items-center group">
                    <img 
                      src={event.image}
                      alt={event.title}
                      className="w-20 h-20 rounded object-cover flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${getEventTypeColor(event.type)} mb-1`}>
                        {event.type}
                      </span>
                      <h3 className="font-display text-lg text-[#1A1A18] group-hover:text-[#B8962F] transition-colors truncate">
                        {event.title}
                      </h3>
                      <div className="flex items-center gap-3 text-xs text-[#8A8A80]">
                        <span>{event.date}</span>
                        <span>{event.time}</span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="btn-outline-gold flex-shrink-0">
                      Details
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Calendar */}
            <div>
              <h2 className="font-display text-2xl text-[#1A1A18] mb-6">Calendar</h2>
              <div className="card-ivory rounded-lg p-4">
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  className="rounded-md"
                />
              </div>

              {/* Past Events */}
              <div className="mt-8">
                <h3 className="font-display text-lg text-[#1A1A18] mb-4">Past Events</h3>
                <div className="space-y-3">
                  {pastEvents.map((event, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-[#E8E8E0]">
                      <div>
                        <p className="text-sm text-[#1A1A18]">{event.title}</p>
                        <p className="text-xs text-[#8A8A80]">{event.date} • {event.attendees} attended</p>
                      </div>
                      {event.recording && (
                        <Button variant="ghost" size="sm" className="text-[#1A365D]">
                          <Video className="w-4 h-4 mr-1" /> Watch
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="py-20 hero-gradient">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-6">
            Never Miss an Event
          </h2>
          <p className="text-[#4A4A45] text-lg mb-8">
            Subscribe to get notified about upcoming exhibitions, workshops, and exclusive experiences.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-md mx-auto">
            <input 
              type="email"
              placeholder="Enter your email"
              className="input-light flex-1 rounded-lg px-4 py-3"
            />
            <Button className="btn-gold px-8">Subscribe</Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Events;
