const HomePage = () => {
  
  return (
    <div className="space-y-6">

      {/* Content Card */}
      <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Getting Started</h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          This is a sample page layout. Use this pattern to create new pages in your application.
        </p>
        
        <div className="mt-4 space-y-3">
          <div className="rounded-lg bg-indigo-50 dark:bg-indigo-900/30 p-4">
            <h3 className="font-medium text-indigo-900 dark:text-indigo-300">Page Structure</h3>
            <p className="mt-1 text-sm text-indigo-700 dark:text-indigo-400">
              Each page should have a header with title and description, followed by content sections.
            </p>
          </div>
          
          <div className="rounded-lg bg-green-50 dark:bg-green-900/30 p-4">
            <h3 className="font-medium text-green-900 dark:text-green-300">Styling</h3>
            <p className="mt-1 text-sm text-green-700 dark:text-green-400">
              Use Tailwind CSS classes for consistent styling across your application.
            </p>
          </div>
          
          <div className="rounded-lg bg-purple-50 dark:bg-purple-900/30 p-4">
            <h3 className="font-medium text-purple-900 dark:text-purple-300">Components</h3>
            <p className="mt-1 text-sm text-purple-700 dark:text-purple-400">
              Break down complex pages into reusable components for better maintainability.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage