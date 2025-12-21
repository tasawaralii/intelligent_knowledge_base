import { BarChart3, Calendar, Users, BrainIcon, MapPin } from 'lucide-react'

const DashboardPage = () => {
    const stats = [

        {
            title: 'Total Notes',
            value: '100',
            description: 'Your Knowledge Base',
            icon: BrainIcon,
            color: 'bg-green-500',
        },
        {
            title: 'Total People',
            value: '543',
            description: 'Information of a Person',
            icon: Users,
            color: 'bg-blue-500',
        },
        {
            title: 'Total Events',
            value: '12',
            description: 'Your Event Timeline',
            icon: Calendar,
            color: 'bg-purple-500',
        },
        {
            title: 'Total Places',
            value: '78',
            description: 'Info or Event at a Place',
            icon: MapPin,
            color: 'bg-orange-500',
        },
    ]

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="mt-1 text-sm text-gray-500">
                    Welcome back! Here's what's happening today.
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat, index) => {
                    const Icon = stat.icon
                    return (
                        <div
                            key={index}
                            className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md"
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                                    <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
                                    <p className="mt-2 text-sm text-green-600">{stat.description}</p>
                                </div>
                                <div className={`rounded-full ${stat.color} p-3`}>
                                    <Icon className="h-6 w-6 text-white" />
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Content Sections */}
            <div className="grid gap-6 lg:grid-cols-2">
                {/* Recent Activity */}
                <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Recent Activity</h2>
                    <div className="mt-4 space-y-4">
                        {[1, 2, 3, 4].map((item) => (
                            <div key={item} className="flex items-center space-x-3">
                                <div className="h-2 w-2 rounded-full bg-indigo-500"></div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white">Activity item {item}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">2 hours ago</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
                    <div className="mt-4 grid grid-cols-2 gap-4">
                        {['Create New', 'View Reports', 'Manage Users', 'Settings'].map((action, index) => (
                            <button
                                key={index}
                                className="rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 transition hover:bg-indigo-50 dark:hover:bg-indigo-900/30 hover:text-indigo-600 dark:hover:text-indigo-400"
                            >
                                {action}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Chart Section */}
            <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Performance Overview</h2>
                <div className="mt-4 flex h-64 items-center justify-center rounded-lg bg-gray-50 dark:bg-gray-700">
                    <p className="text-gray-500 dark:text-gray-400">Chart placeholder - Add your chart library here</p>
                </div>
            </div>
        </div>
    )
}

export default DashboardPage
