import {Form, Stack, Row, Col, Button} from "React-bootstrap"
import CreatableReactSelect from "react-select/creatable"
import {Link, useNavigate} from "react-router-dom"
import {useRef, FormEvent, useState} from "react"
import {NoteData, Tag} from "./App"
import {v4 as uuidV4 } from "uuid"


type NoteFormProps = {
    onSubmit: (data: NoteData) => void
    onAddTag: (tag: Tag) => void
    availableTags: Tag[]
}


export function NoteForm( {onSubmit, onAddTag, availableTags}: NoteFormProps)
{
    const titleRef = useRef<HTMLInputElement>(null)
    const markdownRef = useRef<HTMLTextAreaElement>(null)
    const [selectedTags, setSelectedTags] = useState<Tag[]>([])
    const navigate = useNavigate()

    function handleSubmit(e:FormEvent){
        e.preventDefault()

        onSubmit(
        {
            /* That's the non-null assertion operator. It is a way to tell the compiler 
            "this expression cannot be null or undefined here, so don't complain about 
            the possibility of it being null or undefined." Sometimes the type checker 
            is unable to make that determination itself. The bang operator tells the 
            compiler to temporarily relax the "not null" constraint that it might 
            otherwise demand. It says to the compiler: "As the developer, 
            I know better than you that this variable cannot be null right now". 
            This was also accomplished because we set 
            titleRef and markdownRef as 'required as textarea'*/
            title: titleRef.current!.value,
            markdown: markdownRef.current!.value,
            tags: selectedTags,
        })
        navigate("..")
    }
    return (
        <Form onSubmit = {handleSubmit}>
            <Stack gap={4}>
               <Row>
                <Col>
                <Form.Group controlId = "title">
                    <Form.Label>Title</Form.Label>
                    <Form.Control ref = {titleRef} required></Form.Control>
                </Form.Group>
                </Col>
                <Col>
                <Form.Group controlId = "tags">
                    <Form.Label>Tags</Form.Label>
                    <CreatableReactSelect
                    onCreateOption = {label => {
                        const newTag = { id: uuidV4(), label}
                        onAddTag(newTag)
                        setSelectedTags(prev => [...prev, newTag])
                    }}
                    value={selectedTags.map(tag => { 
                        return {label:tag.label, value: tag.id}})}
                    options = {availableTags.map(tag => {
                        return {label: tag.label, value: tag.id}
                    })}
                    onChange = { tags => {setSelectedTags(tags.map(tag => { return {label: tag.label, id: tag.value}}))}}
                    isMulti></CreatableReactSelect>
                </Form.Group>
                </Col>
               </Row>
               <Form.Group controlId = "markdown">
                    <Form.Label>Body</Form.Label>
                    <Form.Control ref = {markdownRef} required as ="textarea"  rows ={15}></Form.Control>
                </Form.Group>
                <Stack direction = "horizontal" gap = {2} className = "justify-content-end">
                    <Button type="submit" variant = "primary">Save</Button>
                    <Link to="..">
                        <Button type="button" variant = "outline-secondary">Cancel</Button>
                    </Link>
                </Stack>
            </Stack>
        </Form>
    )
}