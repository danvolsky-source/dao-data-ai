export default function Home() {
  return (
    <main className="min-h-screen bg-[#0B1020] text-white">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-[#09EAB4]">DAO Data AI</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8">
            AI-powered governance analytics platform for DAOs
          </p>
          <p className="text-lg text-gray-400 mb-12">
            Predict proposal outcomes using on-chain and off-chain data
          </p>
          <button className="bg-[#09EAB4] hover:bg-[#07D1A0] text-[#0B1020] font-semibold px-8 py-4 rounded-lg text-lg transition-colors">
            Get Started
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="bg-[#1A2332] p-8 rounded-lg border border-[#2A3342]">
            <h3 className="text-2xl font-bold mb-4 text-[#09EAB4]">On-Chain Analysis</h3>
            <p className="text-gray-400">
              Track and analyze governance proposals, voting patterns, and delegate activity across multiple DAOs.
            </p>
          </div>
          <div className="bg-[#1A2332] p-8 rounded-lg border border-[#2A3342]">
            <h3 className="text-2xl font-bold mb-4 text-[#09EAB4]">AI Predictions</h3>
            <p className="text-gray-400">
              Leverage machine learning to predict proposal outcomes based on historical data and trends.
            </p>
          </div>
          <div className="bg-[#1A2332] p-8 rounded-lg border border-[#2A3342]">
            <h3 className="text-2xl font-bold mb-4 text-[#09EAB4]">Real-Time Insights</h3>
            <p className="text-gray-400">
              Get real-time notifications and analytics to stay informed about DAO governance activities.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
