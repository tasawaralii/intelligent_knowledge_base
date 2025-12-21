'use client'
import { ChevronLeft, Home, LayoutDashboard, LogOut, Settings, Users } from 'lucide-react'
import React, { useState } from 'react'
import { cn } from "../utils/cn"
import SidebarItem from "./sidebar-item"
import { useAuth } from '../context/authContext'
import ProfileAvatar from './Profile-avatar'

interface SidebarProps {
  className?: string
}

const CollapsibleSidebar: React.FC<SidebarProps> = ({ className }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const {profile} = useAuth()

  const toggleSidebar = () => {
    setIsCollapsed((prev) => !prev)
  }

  const menuItems = [
    { icon: Home, label: 'Home', active: false, slug: '/' },
    { icon: LayoutDashboard, label: 'Dashboard', active: true, slug: '/dashboard' },
    { icon: Users, label: 'Users', active: false, slug: '/user' },
  ]

  const userActions = [
    { icon: Settings, label: 'Settings', active: false, slug: '/settings' },
    { icon: LogOut, label: 'Logout', active: false, slug: '/logout' },
  ]

  return (
    <aside
      className={cn(
        'flex h-screen flex-col border-r border-r-[#EBEDEE] bg-[#F5F7F9]',
        isCollapsed ? 'w-20' : 'w-60',
        className,
      )}
    >
      {/* Header */}
      <div className="relative border-b border-b-[#EBEDEE] px-4 py-3">
        <div className="flex items-center space-x-3">
          <img
            src="https://plus.unsplash.com/premium_photo-1661962960694-0b4ed303744f?q=80&w=1935&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            alt="App Name Logo"
            className="size-6 rounded-full"
          />
          <span
            className={cn(
              'text-lg font-bold text-gray-800 transition-opacity duration-200',
              isCollapsed && 'hidden opacity-0',
            )}
          >
            Knowledge Base
          </span>
        </div>
        <button
          onClick={toggleSidebar}
          aria-label="Toggle Sidebar"
          className="absolute top-4 -right-3 cursor-pointer rounded-full border border-[#EBEDEE] bg-white p-1 text-gray-600 hover:bg-[#EBEDEE]"
        >
          <ChevronLeft
            className={cn('h-4 w-4 transition-transform duration-200', isCollapsed && 'rotate-180')}
          />
        </button>
      </div>

      {/* Navigation */}
      <nav className="mt-2 flex-1">
        <ul className="space-y-2 px-2">
          {menuItems.map((item, idx) => (
            <li key={idx}>
              <SidebarItem {...item} isCollapsed={isCollapsed} />
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer/User Section */}
      <div className="mt-auto border-t border-t-[#EBEDEE]">
        {/* User Profile */}
        <div className="flex cursor-pointer items-center px-4 py-3 transition hover:bg-gray-100">
          <ProfileAvatar name={profile?.username} />

          <div
            className={cn(
              'ml-3 flex flex-col transition-opacity duration-200',
              isCollapsed && 'hidden opacity-0',
            )}
          >
            <span className="text-sm font-medium text-gray-700">{profile?.first_name} {profile?.last_name}</span>
            <span className="text-xs text-gray-500">{profile?.email}</span>
          </div>
        </div>

        {/* User Actions */}
        <div className="px-2 pb-2">
          {userActions.map((item, idx) => (
            <SidebarItem key={idx} {...item} isCollapsed={isCollapsed} />
          ))}
        </div>

        {/* Footer */}
        <div className="border-t border-t-[#EBEDEE] px-4 py-3">
          <span
            className={cn(
              'text-xs text-gray-400 transition-opacity duration-200',
              isCollapsed && 'hidden opacity-0',
            )}
          >
            © 2025 Knowledge Base
          </span>
        </div>
      </div>
    </aside>
  )
}

export default CollapsibleSidebar