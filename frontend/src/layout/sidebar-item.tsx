import { cn } from "../utils/cn"
import { Link, useLocation } from "react-router-dom"

interface SidebarItemProps {
    icon: React.ElementType
    label: string
    active?: boolean
    isCollapsed: boolean
    slug: string
}

const SidebarItem: React.FC<SidebarItemProps> = ({
    icon: Icon,
    label,
    isCollapsed,
    slug = '#',
}) => {
    const location = useLocation()
    const isActive = location.pathname === slug

    return (
        <Link
            to={slug}
            className={cn(
                'group flex items-center rounded px-4 py-2 text-sm transition',
                isActive
                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400',
            )}
        >
            <Icon
                className={cn(
                    'size-4 flex-shrink-0 transition-colors',
                    isActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500 group-hover:text-blue-600 dark:group-hover:text-blue-400',
                )}
            />
            <span
                className={cn(
                    'ml-4 font-medium transition-opacity duration-200',
                    isCollapsed && 'hidden opacity-0',
                )}
            >
                {label}
            </span>
        </Link>
    )
}

export default SidebarItem