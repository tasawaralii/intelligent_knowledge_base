import { cn } from "../utils/cn"
import { Link } from "react-router-dom"

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
    active = false,
    isCollapsed,
    slug = '#',
}) => {
    return (
        <Link
            to={slug}
            className={cn(
                'group flex items-center rounded px-4 py-2 text-sm transition',
                active
                    ? 'bg-indigo-50 dark:bg-indigo-900/30 text-gray-600 dark:text-gray-300'
                    : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-indigo-600 dark:hover:text-indigo-400',
            )}
        >
            <Icon
                className={cn(
                    'size-4 flex-shrink-0 transition-colors',
                    active ? 'text-gray-800 dark:text-gray-200' : 'text-gray-400 dark:text-gray-500 group-hover:text-indigo-600 dark:group-hover:text-indigo-400',
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