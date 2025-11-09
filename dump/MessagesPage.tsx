import React, { useState, useEffect, useRef } from "react"

import { Input } from "./ui/input"

import { Button } from "./ui/button"

import { Badge } from "./ui/badge"

import { Textarea } from "./ui/textarea"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"

import { ScrollArea } from "./ui/scroll-area"

import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog"

import { Label } from "./ui/label"

import { Search, Instagram, Mail, MessageCircle, Send, Loader2, AlertCircle, Plus, Trash2, Tag } from "lucide-react"

import { useMessages } from "../hooks/useMessages"

import type { ConversationCategory } from "../types/api"



const CATEGORY_CONFIG = {

  consulta: { label: "Consulta", color: "#3b82f6", bgColor: "#dbeafe" },

  pedido: { label: "Pedido", color: "#10b981", bgColor: "#d1fae5" },

  reclamo: { label: "Reclamo", color: "#ef4444", bgColor: "#fee2e2" },

  sin_categoria: { label: "Sin categoría", color: "#6b7280", bgColor: "#f3f4f6" },

}



export function MessagesPage() {

  const {

    conversations,

    selectedConversation,

    setSelectedConversation,

    isLoading,

    error,

    sendMessage,

    markMessageAsRead,

    isConnected,

    updateConversationCategory,

  } = useMessages()



  const [filter, setFilter] = useState<string>("all")

  const [reply, setReply] = useState("")

  const [searchQuery, setSearchQuery] = useState("")

  const [isSending, setIsSending] = useState(false)

  const [categoryFilter, setCategoryFilter] = useState<string>("all")



  const scrollRef = useRef<HTMLDivElement>(null)



  const [templates, setTemplates] = useState([

    { id: "1", name: "Saludo inicial", content: "Hola, gracias por contactarnos. ¿En qué podemos ayudarte?" },

    {

      id: "2",

      name: "Consulta de producto",

      content: "Gracias por tu interés en nuestros productos. Te proporcionaré toda la información que necesites.",

    },

    { id: "3", name: "Estado de pedido", content: "Voy a revisar el estado de tu pedido y te informo en breve." },

    { id: "4", name: "Despedida", content: "Gracias por contactarnos. ¡Que tengas un excelente día!" },

  ])



  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const [newTemplateName, setNewTemplateName] = useState("")

  const [newTemplateContent, setNewTemplateContent] = useState("")



  const handleTemplateSelect = (templateContent: string) => {

    setReply(templateContent)

  }



  const handleSendMessage = async () => {

    if (!reply.trim() || !selectedConversation) return

    setIsSending(true)

    try {

      await sendMessage(selectedConversation.id, reply)

      setReply("")

    } catch (error) {

      console.error("Error sending message:", error)

    } finally {

      setIsSending(false)

    }

  }



  const handleCreateTemplate = () => {

    if (!newTemplateName.trim() || !newTemplateContent.trim()) return

    const newTemplate = {

      id: Date.now().toString(),

      name: newTemplateName,

      content: newTemplateContent,

    }

    setTemplates([...templates, newTemplate])

    setNewTemplateName("")

    setNewTemplateContent("")

    setIsDialogOpen(false)

  }



  const handleDeleteTemplate = (id: string) => {

    setTemplates(templates.filter((t) => t.id !== id))

  }



  const handleCategoryChange = (category: ConversationCategory) => {

    if (selectedConversation) {

      updateConversationCategory(selectedConversation.id, category)

    }

  }



  useEffect(() => {

    if (selectedConversation && selectedConversation.conversation.length > 0) {

      const unreadMessages = selectedConversation.conversation.filter((msg) => msg.sender === "user" && !msg.isRead)

      unreadMessages.forEach((msg) => {

        if (msg.messageId) markMessageAsRead(msg.messageId.toString())

      })

    }

  }, [selectedConversation, markMessageAsRead])



  useEffect(() => {

    if (scrollRef.current) {

      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })

    }

  }, [selectedConversation?.conversation])



  const platformIcons = {

    instagram: <Instagram className="h-4 w-4" />,

    whatsapp: <MessageCircle className="h-4 w-4" />,

    gmail: <Mail className="h-4 w-4" />,

  }



  const platformColors = {

    instagram: "#e4405f",

    whatsapp: "#25d366",

    gmail: "#ea4335",

  }



  const filteredConversations = conversations

    .filter((conv) => (filter === "all" ? true : conv.platform === filter))

    .filter((conv) => (categoryFilter === "all" ? true : (conv.category || "sin_categoria") === categoryFilter))

    .filter((conv) => {

      if (!searchQuery) return true

      const query = searchQuery.toLowerCase()

      return (

        conv.participantName.toLowerCase().includes(query) ||

        conv.lastMessage.toLowerCase().includes(query) ||

        conv.conversation.some((chat) => chat.text.toLowerCase().includes(query))

      )

    })



  if (isLoading) {

    return (

      <div className="h-screen flex items-center justify-center">

        <div className="text-center">

          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />

          <p>Cargando conversaciones...</p>

        </div>

      </div>

    )

  }



  return (

    <div className="h-screen flex flex-col bg-gradient-to-br from-pink-50/30 to-green-50/30">

      <div className="border-b bg-white/80 backdrop-blur-sm px-6 py-4 flex-shrink-0">

        <div className="flex items-center justify-between">

          <div>

            <h2>Mensajes</h2>

            <p className="text-sm text-muted-foreground mt-1">Gestiona todos tus mensajes en un solo lugar</p>

            <div className="flex items-center gap-2 mt-2">

              <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-orange-500"}`} />

              <span className="text-xs text-muted-foreground">

                {isConnected ? "Conectado al backend" : "Modo demo - Backend no configurado"}

              </span>

            </div>

          </div>

        </div>

      </div>



      <div className="flex-1 flex overflow-hidden min-h-0">

        {/* Sidebar */}

        <div className="w-96 border-r bg-white/50 backdrop-blur-sm flex flex-col">

          <div className="p-4 border-b flex-shrink-0 space-y-3">

            <div className="relative">

              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />

              <Input

                placeholder="Buscar mensajes..."

                className="pl-10 rounded-xl"

                value={searchQuery}

                onChange={(e) => setSearchQuery(e.target.value)}

              />

            </div>



            <Select value={categoryFilter} onValueChange={setCategoryFilter}>

              <SelectTrigger className="rounded-xl">

                <div className="flex items-center gap-2">

                  <Tag className="h-4 w-4" />

                  <SelectValue placeholder="Filtrar por categoría" />

                </div>

              </SelectTrigger>

              <SelectContent>

                <SelectItem value="all">Todas las categorías</SelectItem>

                <SelectItem value="consulta">

                  <div className="flex items-center gap-2">

                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CATEGORY_CONFIG.consulta.color }} />

                    Consulta

                  </div>

                </SelectItem>

                <SelectItem value="pedido">

                  <div className="flex items-center gap-2">

                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CATEGORY_CONFIG.pedido.color }} />

                    Pedido

                  </div>

                </SelectItem>

                <SelectItem value="reclamo">

                  <div className="flex items-center gap-2">

                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CATEGORY_CONFIG.reclamo.color }} />

                    Reclamo

                  </div>

                </SelectItem>

                <SelectItem value="sin_categoria">

                  <div className="flex items-center gap-2">

                    <div

                      className="w-3 h-3 rounded-full"

                      style={{ backgroundColor: CATEGORY_CONFIG.sin_categoria.color }}

                    />

                    Sin categoría

                  </div>

                </SelectItem>

              </SelectContent>

            </Select>

          </div>



          <ScrollArea className="flex-1">

            <div className="p-2 pb-6">

              {error && (

                <div className="p-4 mb-4 bg-red-50 border border-red-200 rounded-xl">

                  <div className="flex items-center gap-2">

                    <AlertCircle className="h-4 w-4 text-red-500" />

                    <span className="text-sm text-red-700">{error}</span>

                  </div>

                </div>

              )}

              {filteredConversations.map((conversation) => {

                const category = conversation.category || "sin_categoria"

                const categoryConfig = CATEGORY_CONFIG[category]



                return (

                  <button

                    key={conversation.id}

                    onClick={() => setSelectedConversation(conversation)}

                    className={`w-full text-left p-4 rounded-xl mb-2 transition-all ${

                      selectedConversation?.id === conversation.id

                        ? "bg-gradient-to-r from-pink-100/50 to-green-100/50 shadow-sm"

                        : "hover:bg-white/80"

                    }`}

                  >

                    <div className="flex items-start justify-between mb-2">

                      <div className="flex items-center gap-2">

                        <span className="font-medium">{conversation.participantName}</span>

                        {conversation.unread && (

                          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: "#ec6c8c" }} />

                        )}

                      </div>

                      <span className="text-xs text-muted-foreground">{conversation.time}</span>

                    </div>

                    <p className="text-sm text-muted-foreground line-clamp-2 mb-2">{conversation.lastMessage}</p>

                    <div className="flex items-center gap-2 flex-wrap">

                      <div

                        className="flex items-center gap-1 text-xs"

                        style={{ color: platformColors[conversation.platform] }}

                      >

                        {platformIcons[conversation.platform]}

                        <span className="capitalize">{conversation.platform}</span>

                      </div>

                      <Badge

                        variant="secondary"

                        className="text-xs rounded-full"

                        style={{

                          backgroundColor: categoryConfig.bgColor,

                          color: categoryConfig.color,

                          border: "none",

                        }}

                      >

                        {categoryConfig.label}

                      </Badge>

                    </div>

                  </button>

                )

              })}

            </div>

          </ScrollArea>

        </div>



        {/* Chat View */}

        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

          {selectedConversation ? (

            <>

              <div className="border-b bg-white/80 backdrop-blur-sm px-6 py-4 flex-shrink-0">

                <div className="flex items-center justify-between">

                  <div>

                    <h3>{selectedConversation.participantName}</h3>

                    <div className="flex items-center gap-2 mt-1 flex-wrap">

                      <Badge

                        variant="outline"

                        className="rounded-full"

                        style={{

                          borderColor: platformColors[selectedConversation.platform],

                          color: platformColors[selectedConversation.platform],

                        }}

                      >

                        {platformIcons[selectedConversation.platform]}

                        <span className="ml-1 capitalize">{selectedConversation.platform}</span>

                      </Badge>

                      {selectedConversation.category && (

                        <Badge

                          variant="secondary"

                          className="rounded-full"

                          style={{

                            backgroundColor: CATEGORY_CONFIG[selectedConversation.category].bgColor,

                            color: CATEGORY_CONFIG[selectedConversation.category].color,

                            border: "none",

                          }}

                        >

                          <Tag className="h-3 w-3 mr-1" />

                          {CATEGORY_CONFIG[selectedConversation.category].label}

                        </Badge>

                      )}

                    </div>

                  </div>



                  <div className="flex items-center gap-2">

                    <Label className="text-sm text-muted-foreground">Categoría:</Label>

                    <Select

                      value={selectedConversation.category || "sin_categoria"}

                      onValueChange={(value) => handleCategoryChange(value as ConversationCategory)}

                    >

                      <SelectTrigger className="w-40 rounded-xl">

                        <SelectValue />

                      </SelectTrigger>

                      <SelectContent>

                        <SelectItem value="consulta">

                          <div className="flex items-center gap-2">

                            <div

                              className="w-3 h-3 rounded-full"

                              style={{ backgroundColor: CATEGORY_CONFIG.consulta.color }}

                            />

                            Consulta

                          </div>

                        </SelectItem>

                        <SelectItem value="pedido">

                          <div className="flex items-center gap-2">

                            <div

                              className="w-3 h-3 rounded-full"

                              style={{ backgroundColor: CATEGORY_CONFIG.pedido.color }}

                            />

                            Pedido

                          </div>

                        </SelectItem>

                        <SelectItem value="reclamo">

                          <div className="flex items-center gap-2">

                            <div

                              className="w-3 h-3 rounded-full"

                              style={{ backgroundColor: CATEGORY_CONFIG.reclamo.color }}

                            />

                            Reclamo

                          </div>

                        </SelectItem>

                        <SelectItem value="sin_categoria">

                          <div className="flex items-center gap-2">

                            <div

                              className="w-3 h-3 rounded-full"

                              style={{ backgroundColor: CATEGORY_CONFIG.sin_categoria.color }}

                            />

                            Sin categoría

                          </div>

                        </SelectItem>

                      </SelectContent>

                    </Select>

                  </div>

                </div>

              </div>



              <div ref={scrollRef} className="flex-1 overflow-y-auto p-6">

                <div className="space-y-4 max-w-3xl pb-6">

                  {selectedConversation.conversation.map((chat) => (

                    <div key={chat.id} className={`flex gap-3 ${chat.sender === "me" ? "flex-row-reverse" : ""}`}>

                      <div

                        className={`w-8 h-8 rounded-full flex items-center justify-center text-white flex-shrink-0 ${

                          chat.sender === "me" ? "bg-gradient-to-br from-pink-400 to-green-400" : ""

                        }`}

                        style={chat.sender === "user" ? { backgroundColor: "#ec6c8c" } : {}}

                      >

                        {chat.sender === "me" ? "Yo" : selectedConversation.participantName.charAt(0)}

                      </div>

                      <div className="flex-1 max-w-lg">

                        <div

                          className={`rounded-2xl p-4 shadow-sm ${

                            chat.sender === "me"

                              ? "bg-gradient-to-br from-pink-100 to-green-100 rounded-tr-sm"

                              : "bg-white rounded-tl-sm"

                          }`}

                        >

                          <p>{chat.text}</p>

                        </div>

                        <span className="text-xs text-muted-foreground mt-1 ml-1 block">{chat.time}</span>

                      </div>

                    </div>

                  ))}

                </div>

              </div>



              {/* Área de plantillas + entrada */}

              <div className="border-t bg-white/80 backdrop-blur-sm p-6 flex-shrink-0">

                <div className="max-w-3xl space-y-4">

                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 justify-between">

                    <div className="flex items-center gap-2">

                      <span className="text-sm text-muted-foreground">Plantilla:</span>

                      <Select

                        onValueChange={(value) => {

                          const template = templates.find((t) => t.id === value)

                          if (template) handleTemplateSelect(template.content)

                        }}

                      >

                        <SelectTrigger className="w-64 rounded-xl">

                          <SelectValue placeholder="Seleccionar plantilla" />

                        </SelectTrigger>

                        <SelectContent>

                          {templates.map((template) => (

                            <div key={template.id} className="flex items-center justify-between">

                              <SelectItem value={template.id}>{template.name}</SelectItem>

                              <Button

                                variant="ghost"

                                size="icon"

                                className="h-6 w-6 text-red-500 hover:bg-red-100"

                                onClick={(e) => {

                                  e.stopPropagation()

                                  handleDeleteTemplate(template.id)

                                }}

                              >

                                <Trash2 className="h-4 w-4" />

                              </Button>

                            </div>

                          ))}

                        </SelectContent>

                      </Select>

                    </div>

                    <Button

                      onClick={() => setIsDialogOpen(true)}

                      variant="outline"

                      className="rounded-xl flex items-center gap-2"

                    >

                      <Plus className="h-4 w-4" /> Nuevo

                    </Button>

                  </div>



                  <div className="flex gap-2 items-end">

                    <Textarea

                      placeholder="Escribe tu respuesta..."

                      value={reply}

                      onChange={(e) => setReply(e.target.value)}

                      className="rounded-xl resize-none flex-1 min-h-[90px] text-base"

                      rows={4}

                      onKeyDown={(e) => {

                        if (e.key === "Enter" && !e.shiftKey) {

                          e.preventDefault()

                          handleSendMessage()

                        }

                      }}

                      disabled={isSending}

                    />

                    <Button

                      className="rounded-xl h-auto px-4 py-6"

                      style={{ backgroundColor: "#acce60" }}

                      onClick={handleSendMessage}

                      disabled={!reply.trim() || isSending}

                    >

                      {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-5 w-5" />}

                    </Button>

                  </div>

                </div>

              </div>

            </>

          ) : (

            <div className="flex-1 flex items-center justify-center text-muted-foreground">

              <div className="text-center">

                <MessageCircle className="h-16 w-16 mx-auto mb-4 opacity-20" />

                <p>Selecciona una conversación para ver los mensajes</p>

              </div>

            </div>

          )}

        </div>

      </div>



      {/* Dialog de nueva plantilla */}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>

        <DialogContent className="rounded-2xl">

          <DialogHeader>

            <DialogTitle>Crear nueva plantilla</DialogTitle>

            <DialogDescription>Define un nombre y un mensaje predeterminado.</DialogDescription>

          </DialogHeader>

          <div className="space-y-4 py-4">

            <div className="space-y-2">

              <Label>Nombre de la plantilla</Label>

              <Input

                value={newTemplateName}

                onChange={(e) => setNewTemplateName(e.target.value)}

                placeholder="Ej: Respuesta de envío"

              />

            </div>

            <div className="space-y-2">

              <Label>Mensaje</Label>

              <Textarea

                value={newTemplateContent}

                onChange={(e) => setNewTemplateContent(e.target.value)}

                placeholder="Escribe el mensaje predeterminado..."

                rows={4}

              />

            </div>

          </div>

          <DialogFooter>

            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>

              Cancelar

            </Button>

            <Button

              onClick={handleCreateTemplate}

              style={{ backgroundColor: "#ec6c8c" }}

              disabled={!newTemplateName.trim() || !newTemplateContent.trim()}

            >

              Crear

            </Button>

          </DialogFooter>

        </DialogContent>

      </Dialog>

    </div>

  )

}
