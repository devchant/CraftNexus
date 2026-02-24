
"use client";
import { useState } from "react";
import { FaBars, FaTimes } from "react-icons/fa";

type MarketSection = "courses" | "workshops" | "tools" | "materials";

const sections = [
  { id: "courses" as MarketSection, label: "Courses", description: "Browse available courses" },
  { id: "workshops" as MarketSection, label: "Workshops", description: "Join interactive workshops" },
  { id: "tools" as MarketSection, label: "Tools", description: "Find essential crafting tools" },
  { id: "materials" as MarketSection, label: "Materials", description: "Shop for crafting materials" },
];

const sectionContent = {
  courses: {
    title: "Courses",
    content: "Explore our comprehensive collection of crafting courses. From beginner to advanced levels, find the perfect course to enhance your skills."
  },
  workshops: {
    title: "Workshops",
    content: "Join live interactive workshops led by expert craftsmen. Learn hands-on techniques and get real-time feedback from instructors."
  },
  tools: {
    title: "Tools",
    content: "Discover high-quality crafting tools from trusted manufacturers. Find everything you need for your next project."
  },
  materials: {
    title: "Materials",
    content: "Shop our curated selection of premium crafting materials. From fabrics to metals, we have everything you need."
  }
};

export default function Market() {
  const [activeSection, setActiveSection] = useState<MarketSection>("courses");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const selectSection = (section: MarketSection) => {
    setActiveSection(section);
    setIsSidebarOpen(false); // Close sidebar on mobile after selection
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Mobile Sidebar Toggle */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={toggleSidebar}
          className="bg-white p-2 rounded-lg shadow-md"
        >
          {isSidebarOpen ? (
            <FaTimes className="text-gray-800 text-xl" />
          ) : (
            <FaBars className="text-gray-800 text-xl" />
          )}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        fixed md:relative top-0 left-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out z-40
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:translate-x-0 md:shadow-none
      `}>
        <div className="p-6 pt-16 md:pt-6">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">Market</h2>
          <nav className="space-y-2">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => selectSection(section.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors duration-200 ${
                  activeSection === section.id
                    ? "bg-blue-100 text-blue-700 font-semibold"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                <div className="font-medium">{section.label}</div>
                <div className="text-sm text-gray-500 mt-1">{section.description}</div>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 ml-0 md:ml-64 p-6 pt-16 md:pt-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">
              {sectionContent[activeSection].title}
            </h1>
            <p className="text-gray-600 text-lg leading-relaxed">
              {sectionContent[activeSection].content}
            </p>

            {/* Placeholder for section-specific content */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Sample cards - replace with actual content */}
              {[1, 2, 3, 4, 5, 6].map((item) => (
                <div key={item} className="bg-gray-50 p-4 rounded-lg border">
                  <div className="h-32 bg-gray-200 rounded mb-3"></div>
                  <h3 className="font-semibold text-gray-800">Item {item}</h3>
                  <p className="text-gray-600 text-sm">Description for item {item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
