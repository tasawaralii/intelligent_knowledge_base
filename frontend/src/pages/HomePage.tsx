const HomePage = () => {
  
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Home</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to your application home page.
        </p>
      </div>

      {/* Content Card */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-900">Getting Started</h2>
        <p className="mt-2 text-gray-600">
          This is a sample page layout. Use this pattern to create new pages in your application.
        </p>
        
        <div className="mt-4 space-y-3">
          <div className="rounded-lg bg-indigo-50 p-4">
            <h3 className="font-medium text-indigo-900">Page Structure</h3>
            <p className="mt-1 text-sm text-indigo-700">
              Each page should have a header with title and description, followed by content sections.
            </p>
          </div>
          
          <div className="rounded-lg bg-green-50 p-4">
            <h3 className="font-medium text-green-900">Styling</h3>
            <p className="mt-1 text-sm text-green-700">
              Use Tailwind CSS classes for consistent styling across your application.
            </p>
          </div>
          
          <div className="rounded-lg bg-purple-50 p-4">
            <h3 className="font-medium text-purple-900">Components</h3>
            <p className="mt-1 text-sm text-purple-700">
              Break down complex pages into reusable components for better maintainability.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage